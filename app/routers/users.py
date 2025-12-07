# app/routers/users.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..schemas import UserCreate, UserUpdate, UserRead
from ..core.security import get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [UserRead.model_validate(u) for u in users]


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    # check email unique
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use",
        )

    role = db.query(models.Role).get(body.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id",
        )

    user = models.User(
        full_name=body.full_name,
        email=body.email,
        password_hash=get_password_hash(body.password),
        is_active=True,
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # full_name
    if body.full_name is not None:
        user.full_name = body.full_name

    # email + unique check
    if body.email is not None and body.email != user.email:
        existing = db.query(models.User).filter(models.User.email == body.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = body.email

    # active flag
    if body.is_active is not None:
        user.is_active = body.is_active

    # role change
    if body.role_id is not None:
        role = db.query(models.Role).get(body.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id",
            )
        user.role = role

    # password change
    if body.password:
        user.password_hash = get_password_hash(body.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)
