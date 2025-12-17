from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.department import Department
from app.schemas.department import (
    DepartmentRead,
    DepartmentCreate,
    DepartmentUpdate,
)

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    return [DepartmentRead.model_validate(d) for d in depts]


@router.post("", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db)):
    if db.query(Department).filter(Department.name == body.name).first():
        raise HTTPException(status_code=400, detail="Department already exists")

    dept = Department(
        name=body.name,
        description=body.description,
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return DepartmentRead.model_validate(dept)


@router.put("/{dept_id}", response_model=DepartmentRead)
def update_department(
    dept_id: int,
    body: DepartmentUpdate,
    db: Session = Depends(get_db),
):
    dept = db.query(Department).get(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    if body.name is not None:
        dept.name = body.name
    if body.description is not None:
        dept.description = body.description
    if body.is_active is not None:
        dept.is_active = body.is_active

    db.add(dept)
    db.commit()
    db.refresh(dept)
    return DepartmentRead.model_validate(dept)
