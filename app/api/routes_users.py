from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserRead, UserCreate, UserUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])


# ==========================
# Helper: Generate Employee ID
# ==========================
def generate_employee_id(db: Session) -> str:
    """
    Generate a new employee ID like:
    AW001, AW002, AW003, ...

    Uses the last user's ID to compute the next number.
    """
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
    # Check username unique
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already in use",
        )

    # Check email unique
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use",
        )

    # Check role valid
    role = db.query(Role).get(body.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id",
        )

    # Generate emp_id like AW001, AW002, ...
    new_emp_id = generate_employee_id(db)

    user = User(
        emp_id=new_emp_id,
        username=body.username,
        full_name=body.full_name,
        email=body.email,
        dept=body.dept,
        is_active=True,
        role=role,
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

    # username
    if body.username is not None and body.username != user.username:
        existing = db.query(User).filter(User.username == body.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use",
            )
        user.username = body.username

    # full_name
    if body.full_name is not None:
        user.full_name = body.full_name

    # email (with uniqueness check)
    if body.email is not None and body.email != user.email:
        existing = db.query(User).filter(User.email == body.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = body.email

    # dept
    if body.dept is not None:
        user.dept = body.dept

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
