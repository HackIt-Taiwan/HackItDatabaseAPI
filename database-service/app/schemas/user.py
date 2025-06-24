from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    user_id: int
    guild_id: int
    real_name: str
    email: EmailStr
    source: Optional[str] = None
    education_stage: Optional[str] = None
    avatar_base64: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass

class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    real_name: Optional[str] = None
    source: Optional[str] = None
    education_stage: Optional[str] = None
    avatar_base64: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    registered_at: Optional[str] = None

    class Config:
        from_attributes = True

class UserQuery(BaseModel):
    """Schema for user query parameters."""
    email: Optional[EmailStr] = None
    user_id: Optional[int] = None
    guild_id: Optional[int] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0

class APIResponse(BaseModel):
    """Generic API response schema."""
    success: bool
    message: str
    data: Optional[dict] = None 