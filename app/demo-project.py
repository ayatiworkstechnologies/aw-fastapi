# backend/main.py
import os
import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

from passlib.context import CryptContext
import jwt


# ==========================
# CONFIG
# ==========================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:ruban@localhost:3306/aw_admin?charset=utf8mb4",
)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

# SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Password hashing – use pbkdf2, not bcrypt
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# ==========================
# MODELS
# ==========================

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")

    # helper methods
    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)


# ==========================
# SCHEMAS (Pydantic)
# ==========================

# ---- Roles ----
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleRead(RoleBase):
    id: int

    class Config:
        from_attributes = True

# ---- Users ----
class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role_id: int


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None


class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    role: Optional[RoleRead]

    class Config:
        from_attributes = True


# ---- Auth ----
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
    user: UserRead


# ==========================
# DB DEPENDENCY
# ==========================

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()


# ==========================
# JWT UTILS
# ==========================

def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# ==========================
# FASTAPI APP
# ==========================

app = FastAPI(title="Simple AW Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # change as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================
# STARTUP: CREATE TABLES + SEED
# ==========================

def seed_initial_data(db: Session):
    # Seed roles if empty
    if db.query(Role).count() == 0:
        default_roles = [
            ("admin", "Full access"),
            ("employee", "Standard employee"),
            ("hr", "HR staff"),
            ("manager", "Team manager"),
        ]
        for name, desc in default_roles:
            db.add(Role(name=name, description=desc))
        db.commit()

    # Seed one Super Admin if no users
    if db.query(User).count() == 0:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            admin = User(
                full_name="Super Admin",
                email="admin@example.com",
                is_active=True,
                role=admin_role,
            )
            admin.set_password("admin123")  # default password
            db.add(admin)
            db.commit()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()


# ==========================
# ROUTES – AUTH (NO ROLE CHECK)
# ==========================

@app.post("/api/auth/login", response_model=TokenResponse)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    """
    Simple login:
    - checks email & password
    - returns JWT token + user
    """
    user = db.query(User).filter(User.email == creds.email).first()
    if not user or not user.check_password(creds.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(user)
    return TokenResponse(token=token, user=UserRead.model_validate(user))


# ==========================
# ROUTES – ROLES (OPEN)
# ==========================

@app.get("/api/roles", response_model=List[RoleRead])
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [RoleRead.model_validate(r) for r in roles]


@app.post("/api/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(body: RoleCreate, db: Session = Depends(get_db)):
    if db.query(Role).filter(Role.name == body.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists",
        )

    role = Role(name=body.name, description=body.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleRead.model_validate(role)


# ==========================
# ROUTES – USERS (OPEN)
# ==========================

@app.get("/api/users", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserRead.model_validate(u) for u in users]


@app.post("/api/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    # check email unique
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use",
        )

    # check role
    role = db.query(Role).get(body.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id",
        )

    user = User(
        full_name=body.full_name,
        email=body.email,
        is_active=True,
        role=role,
    )
    user.set_password(body.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@app.get("/api/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@app.put("/api/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    """
    Update user (partial):
    - full_name
    - email (with uniqueness check)
    - password (rehash)
    - is_active
    - role_id
    """
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # full_name
    if body.full_name is not None:
        user.full_name = body.full_name

    # email (check unique)
    if body.email is not None and body.email != user.email:
        existing = db.query(User).filter(User.email == body.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = body.email

    # is_active
    if body.is_active is not None:
        user.is_active = body.is_active

    # role
    if body.role_id is not None:
        role = db.query(Role).get(body.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id",
            )
        user.role = role

    # password change
    if body.password:
        user.set_password(body.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@app.put("/api/roles/{role_id}", response_model=RoleRead)
def update_role(role_id: int, body: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # update fields only if provided
    if body.name is not None:
        role.name = body.name
    if body.description is not None:
        role.description = body.description

    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleRead.model_validate(role)


# ==========================
# MAIN (for `python main.py`)
# ==========================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
