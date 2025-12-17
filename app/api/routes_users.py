from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import User
from app.models.role import Role
from app.models.department import Department
from app.schemas.user import UserRead, UserCreate, UserUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])


# ==========================
# Generate Employee ID
# ==========================
def generate_employee_id(db: Session) -> str:
    last_user = db.query(User).order_by(User.id.desc()).first()
    next_number = (last_user.id if last_user else 0) + 1
    return f"AW{str(next_number).zfill(3)}"


# ==========================
# LIST USERS
# ==========================
@router.get("", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserRead.model_validate(u) for u in users]


# ==========================
# CREATE USER
# ==========================
@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already in use")

    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already in use")

    role = db.query(Role).get(body.role_id)
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role_id")

    department = None
    if body.department_id:
        department = db.query(Department).get(body.department_id)
        if not department:
            raise HTTPException(status_code=400, detail="Invalid department_id")

    user = User(
        emp_id=generate_employee_id(db),
        username=body.username,
        full_name=body.full_name,
        email=body.email,
        is_active=True,
        role=role,
        department=department,   # ✅ FIX
    )
    user.set_password(body.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


# ==========================
# GET SINGLE USER
# ==========================
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


# ==========================
# UPDATE USER
# ==========================
@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.username and body.username != user.username:
        if db.query(User).filter(User.username == body.username).first():
            raise HTTPException(status_code=400, detail="Username already in use")
        user.username = body.username

    if body.full_name is not None:
        user.full_name = body.full_name

    if body.email and body.email != user.email:
        if db.query(User).filter(User.email == body.email).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = body.email

    if body.department_id is not None:
        dept = db.query(Department).get(body.department_id)
        if not dept:
            raise HTTPException(status_code=400, detail="Invalid department_id")
        user.department = dept

    if body.is_active is not None:
        user.is_active = body.is_active

    if body.role_id is not None:
        role = db.query(Role).get(body.role_id)
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role_id")
        user.role = role

    if body.password:
        user.set_password(body.password)

    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)
