# app/models/author.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(120), nullable=False, unique=True, index=True)
    role = Column(String(120), nullable=True)            # e.g. "Senior SEO Strategist"
    bio = Column(Text, nullable=True)
    avatar = Column(String(1024), nullable=True)         # avatar url
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    blogs = relationship("Blog", back_populates="author", cascade="all, delete-orphan")
