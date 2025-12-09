from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.role import Role
from app.schemas.role import RoleRead, RoleCreate, RoleUpdate

router = APIRouter(prefix="/api/roles", tags=["Roles"])

@router.get("", response_model=List[RoleRead])
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [RoleRead.model_validate(r) for r in roles]

@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(body: RoleCreate, db: Session = Depends(get_db)):
    if db.query(Role).filter(Role.name == body.name).first():
        raise HTTPException(status_code=400, detail="Role already exists")

    role = Role(name=body.name, description=body.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleRead.model_validate(role)

@router.put("/{role_id}", response_model=RoleRead)
def update_role(role_id: int, body: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if body.name is not None:
        role.name = body.name
    if body.description is not None:
        role.description = body.description

    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleRead.model_validate(role)
