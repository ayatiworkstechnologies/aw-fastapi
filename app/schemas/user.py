from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas.role import RoleRead

class UserBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    dept: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: int

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    dept: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None

class UserRead(BaseModel):
    id: int
    emp_id: str
    username: str
    full_name: str
    email: EmailStr
    dept: Optional[str]
    is_active: bool
    role: Optional[RoleRead]

    class Config:
        from_attributes = True
