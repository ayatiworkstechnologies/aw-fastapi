from pydantic import BaseModel, EmailStr
from app.schemas.user import UserRead

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    user: UserRead
