from typing import Optional
from pydantic import BaseModel

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DepartmentRead(DepartmentBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
