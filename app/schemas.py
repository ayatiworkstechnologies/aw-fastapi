# app/schemas.py
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# ========== ROLE SCHEMAS ==========

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
        from_attributes = True  # works with SQLAlchemy objects


# ========== USER SCHEMAS ==========

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


# ========== AUTH SCHEMAS ==========

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
    user: UserRead
