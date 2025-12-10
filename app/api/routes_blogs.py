# app/api/routes_blogs.py
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.api.deps import get_db
from app.models.blog import Blog
from app.models.author import Author
from app.models.category import Category
from app.schemas.blog import BlogRead, BlogCreate, BlogUpdate
from app.utils.slugify import slugify

router = APIRouter(prefix="/api/blogs", tags=["Blogs"])


def _normalise_sections(sections: Optional[List[Any]]) -> Optional[List[dict]]:
    """
    Convert Pydantic SectionItem objects (which may contain HttpUrl) into plain dicts
    with serializable values (strings, ints, None). Also ensure an `order` integer.
    """
    if not sections:
        return None

    normalized = []
    for idx, s in enumerate(sections, start=1):
        # s may be a Pydantic model or a plain dict
        if hasattr(s, "dict"):
            item = s.dict()
        else:
            item = dict(s)

        # convert HttpUrl or other objects to str for img/banner fields
        if item.get("img") is not None:
            item["img"] = str(item["img"])
        if item.get("order") is None:
            item["order"] = idx
        else:
            try:
                item["order"] = int(item["order"])
            except Exception:
                item["order"] = idx

        # ensure keys are only primitive types (avoid Pydantic types)
        for k, v in list(item.items()):
            if v is None:
                continue
            if not isinstance(v, (str, int, float, bool, type(None))):
                item[k] = str(v)
        normalized.append(item)
    return normalized


@router.get("", response_model=List[BlogRead])
def list_blogs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(10, le=100),
    q: Optional[str] = Query(None),
    category: Optional[str] = None,
    author: Optional[str] = None,
    published: Optional[bool] = True,
):
    """
    List blogs with optional filters:
    - q: search in title or deck
    - category: category slug
    - author: author slug
    - published: boolean
    Pagination: skip, limit
    """
    query = db.query(Blog).options(joinedload(Blog.author), joinedload(Blog.category_obj))

    if published is not None:
        query = query.filter(Blog.is_published == published)

    if category:
        query = query.join(Category).filter(func.lower(Category.slug) == category.lower())

    if author:
        query = query.join(Author).filter(func.lower(Author.slug) == author.lower())

    if q:
        q_like = f"%{q.lower()}%"
        query = query.filter(
            func.lower(Blog.title).like(q_like) | func.lower(func.coalesce(Blog.deck, "")).like(q_like)
        )

    items = query.order_by(Blog.created_at.desc()).offset(skip).limit(limit).all()
    return [BlogRead.model_validate(b) for b in items]


@router.get("/{slug}", response_model=BlogRead)
def get_blog(slug: str, db: Session = Depends(get_db)):
    blog = (
        db.query(Blog)
        .options(joinedload(Blog.author), joinedload(Blog.category_obj))
        .filter(Blog.slug == slug)
        .first()
    )
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return BlogRead.model_validate(blog)


@router.post("", response_model=BlogRead, status_code=status.HTTP_201_CREATED)
def create_blog(body: BlogCreate, db: Session = Depends(get_db)):
    """
    Create blog:
    - slug generated from title (unique enforced)
    - supports sections (JSON), banner_img/banner_title OR cover/cover_alt
    - validates author_id and category_id
    """
    base = body.slug or slugify(body.title)
    slug = base
    i = 1
    while db.query(Blog).filter(Blog.slug == slug).first():
        i += 1
        slug = f"{base}-{i}"

    # Validate author/category
    author = None
    if body.author_id:
        author = db.query(Author).get(body.author_id)
        if not author:
            raise HTTPException(status_code=400, detail="Invalid author_id")

    category = None
    if body.category_id:
        category = db.query(Category).get(body.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    # Normalize sections (convert HttpUrl -> str etc)
    sections = _normalise_sections(body.sections)

    # Accept both banner_img/banner_title (new) and cover/cover_alt (legacy)
    banner_img = getattr(body, "banner_img", None) or getattr(body, "cover", None)
    banner_title = getattr(body, "banner_title", None) or getattr(body, "cover_alt", None)

    blog = Blog(
        title=body.title,
        slug=slug,
        deck=body.deck,
        # content kept as-is (raw markdown or html depending on your flow)
        content=getattr(body, "content", None),
        # store banner/cover normalized to string
        banner_img=str(banner_img) if banner_img else None,
        cover=str(getattr(body, "cover", None)) if getattr(body, "cover", None) else None,
        banner_title=banner_title,
        cover_alt=getattr(body, "cover_alt", None),
        sections=sections,
        author=author,
        category_obj=category,
        read_mins=body.read_mins,
        is_published=body.is_published,
    )

    if author:
        blog.author_name = author.name
        blog.author_slug = author.slug

    db.add(blog)
    db.commit()
    db.refresh(blog)
    return BlogRead.model_validate(blog)


@router.put("/{slug}", response_model=BlogRead)
def update_blog(slug: str, body: BlogUpdate, db: Session = Depends(get_db)):
    """
    Partial update for blog. Accepts same fields as create.
    If sections provided, they replace existing sections.
    """
    blog = db.query(Blog).filter(Blog.slug == slug).first()
    if not blog:
        raise HTTPException(status_code=404, detail="User not found")

    if body.title is not None:
        blog.title = body.title

    # slug update (optional)
    if body.slug is not None and body.slug != blog.slug:
        if db.query(Blog).filter(Blog.slug == body.slug).first():
            raise HTTPException(status_code=400, detail="Slug already in use")
        blog.slug = body.slug

    if body.deck is not None:
        blog.deck = body.deck

    # banner / cover
    if getattr(body, "banner_img", None) is not None:
        blog.banner_img = str(body.banner_img) if body.banner_img else None
    elif getattr(body, "cover", None) is not None:
        blog.cover = str(body.cover) if body.cover else None

    if getattr(body, "banner_title", None) is not None:
        blog.banner_title = body.banner_title
    elif getattr(body, "cover_alt", None) is not None:
        blog.cover_alt = body.cover_alt

    # sections replace entirely if provided
    if body.sections is not None:
        blog.sections = _normalise_sections(body.sections)

    # author/category changes
    if body.author_id is not None:
        author = db.query(Author).get(body.author_id)
        if not author:
            raise HTTPException(status_code=400, detail="Invalid author_id")
        blog.author = author
        blog.author_name = author.name
        blog.author_slug = author.slug

    if body.category_id is not None:
        category = db.query(Category).get(body.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")
        blog.category_obj = category

    # other simple fields
    for field in ["content", "read_mins", "is_published"]:
        if getattr(body, field, None) is not None:
            setattr(blog, field, getattr(body, field))

    db.add(blog)
    db.commit()
    db.refresh(blog)
    return BlogRead.model_validate(blog)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(slug: str, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.slug == slug).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(blog)
    db.commit()
    return None
