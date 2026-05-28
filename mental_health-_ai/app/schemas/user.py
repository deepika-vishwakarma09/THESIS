
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
 
 
# ── Register ───────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
 
    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v
 
    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v
 
 
# ── Login ──────────────────────────────────────────────────────────────────────
class UserLogin(BaseModel):
    username: str
    password: str
 
 
# ── Response (never expose hashed_password) ───────────────────────────────────
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
 
    model_config = {"from_attributes": True}
 
 
# ── JWT Token ──────────────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
 
 
class TokenData(BaseModel):
    user_id: int | None = None