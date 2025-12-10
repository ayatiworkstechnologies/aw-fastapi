# app/schemas/author.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class AuthorBase(BaseModel):
    name: str
    slug: str
    role: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[HttpUrl] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[HttpUrl] = None

class AuthorRead(AuthorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
