# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..schemas import LoginRequest, TokenResponse, UserRead
from ..core.security import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    """
    Simple login:
    - checks email & password
    - returns JWT token + user data
    """
    user = db.query(models.User).filter(models.User.email == creds.email).first()
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(user_id=user.id, email=user.email)
    user_read = UserRead.model_validate(user)

    return TokenResponse(token=token, user=user_read)
