"""Pydantic models for the application"""

from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user model"""

    username: str
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model"""

    password: str


class User(UserBase):
    """User response model"""

    id: int
    is_active: bool = True

    class Config:
        from_attributes = True


class UserInDB(User):
    """User model for database storage"""

    hashed_password: str


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model"""

    username: Optional[str] = None
