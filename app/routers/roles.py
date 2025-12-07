# app/routers/roles.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..schemas import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("/", response_model=List[RoleRead])
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Role).all()
    return [RoleRead.model_validate(r) for r in roles]


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(body: RoleCreate, db: Session = Depends(get_db)):
    if db.query(models.Role).filter(models.Role.name == body.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists",
        )

    role = models.Role(name=body.name, description=body.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleRead.model_validate(role)


@router.put("/{role_id}", response_model=RoleRead)
def update_role(role_id: int, body: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(models.Role).get(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if body.name is not None:
        role.name = body.name
    if body.description is not None:
        role.description = body.description

    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleRead.model_validate(role)
