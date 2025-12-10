# app/models/blog.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.base import Base  # adjust import if your Base lives elsewhere

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)

    # Banner / cover
    banner_img = Column(String(1024), nullable=True)
    banner_title = Column(String(512), nullable=True)
    cover = Column(String(1024), nullable=True)       # legacy
    cover_alt = Column(String(512), nullable=True)    # legacy

    deck = Column(String(512), nullable=True)   # short description / deck

    # Article body
    content = Column(Text, nullable=True)            # raw markdown or HTML
    content_html = Column(Text, nullable=True)       # optional pre-rendered HTML

    # Sections JSON (list of objects)
    sections = Column(JSON, nullable=True)

    # Foreign keys for author & category
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Denormalised author fields for convenience
    author_name = Column(String(120), nullable=True)
    author_slug = Column(String(120), nullable=True)

    read_mins = Column(Integer, nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("Author", back_populates="blogs")
    category_obj = relationship("Category", back_populates="blogs")
