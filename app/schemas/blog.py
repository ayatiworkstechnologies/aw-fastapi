# app/schemas/blog.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.schemas.author import AuthorRead
from app.schemas.category import CategoryRead


# -----------------------------------------
# Section model (dynamic multi-section blog body)
# -----------------------------------------
class SectionItem(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    img: Optional[str] = None     # ALWAYS store as plain string (NOT HttpUrl)
    order: Optional[int] = None


# -----------------------------------------
# Shared fields
# -----------------------------------------
class BlogBase(BaseModel):
    title: str
    deck: Optional[str] = None

    # Banner fields
    banner_img: Optional[str] = None      # <-- FIXED: must be string
    banner_title: Optional[str] = None

    # Content fields (optional)
    content: Optional[str] = None
    content_html: Optional[str] = None

    read_mins: Optional[int] = None
    is_published: Optional[bool] = True

    author_id: Optional[int] = None
    category_id: Optional[int] = None

    # Multi-section list
    sections: Optional[List[SectionItem]] = None


# -----------------------------------------
# CREATE
# -----------------------------------------
class BlogCreate(BlogBase):
    slug: Optional[str] = None  # auto-generate if not given


# -----------------------------------------
# UPDATE
# -----------------------------------------
class BlogUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    deck: Optional[str] = None

    banner_img: Optional[str] = None
    banner_title: Optional[str] = None

    content: Optional[str] = None
    content_html: Optional[str] = None

    read_mins: Optional[int] = None
    is_published: Optional[bool] = None

    author_id: Optional[int] = None
    category_id: Optional[int] = None

    sections: Optional[List[SectionItem]] = None


# -----------------------------------------
# READ
# -----------------------------------------
class BlogRead(BlogBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    # Full nested objects
    author: Optional[AuthorRead] = None
    category: Optional[CategoryRead] = None

    class Config:
        from_attributes = True   # Required for ORM → Pydantic conversion
