# app/api/routes_authors.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorRead, AuthorUpdate

router = APIRouter(prefix="/api/authors", tags=["Authors"])

@router.get("", response_model=List[AuthorRead])
def list_authors(db: Session = Depends(get_db)):
    authors = db.query(Author).order_by(Author.name).all()
    return [AuthorRead.model_validate(a) for a in authors]

@router.post("", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(body: AuthorCreate, db: Session = Depends(get_db)):
    if db.query(Author).filter(Author.slug == body.slug).first():
        raise HTTPException(status_code=400, detail="Author slug already exists")
    author = Author(
        name=body.name,
        slug=body.slug,
        role=body.role,
        bio=body.bio,
        avatar=str(body.avatar) if body.avatar else None,
    )
    db.add(author)
    db.commit()
    db.refresh(author)
    return AuthorRead.model_validate(author)

@router.get("/{author_id}", response_model=AuthorRead)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).get(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return AuthorRead.model_validate(author)

@router.put("/{author_id}", response_model=AuthorRead)
def update_author(author_id: int, body: AuthorUpdate, db: Session = Depends(get_db)):
    author = db.query(Author).get(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if body.name is not None:
        author.name = body.name
    if body.slug is not None:
        author.slug = body.slug
    if body.role is not None:
        author.role = body.role
    if body.bio is not None:
        author.bio = body.bio
    if body.avatar is not None:
        author.avatar = str(body.avatar)
    db.add(author)
    db.commit()
    db.refresh(author)
    return AuthorRead.model_validate(author)

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).get(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(author)
    db.commit()
    return None
