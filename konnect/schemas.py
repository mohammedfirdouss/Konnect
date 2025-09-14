"""Pydantic schemas for API validation and serialization"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# User schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    """User schema for database storage"""
    hashed_password: str


# Token schemas
class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


# Marketplace schemas
class MarketplaceBase(BaseModel):
    """Base marketplace schema"""
    name: str
    description: Optional[str] = None


class MarketplaceCreate(MarketplaceBase):
    """Marketplace creation schema"""
    pass


class MarketplaceUpdate(BaseModel):
    """Marketplace update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Marketplace(MarketplaceBase):
    """Marketplace response schema"""
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Listing schemas
class ListingBase(BaseModel):
    """Base listing schema"""
    title: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None


class ListingCreate(ListingBase):
    """Listing creation schema"""
    marketplace_id: int


class ListingUpdate(BaseModel):
    """Listing update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class Listing(ListingBase):
    """Listing response schema"""
    id: int
    marketplace_id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schemas with relationships
class MarketplaceWithListings(Marketplace):
    """Marketplace schema with listings"""
    listings: List[Listing] = []


class UserWithDetails(User):
    """User schema with marketplaces and listings"""
    marketplaces: List[Marketplace] = []
    listings: List[Listing] = []


# Purchase schemas
class PurchaseBase(BaseModel):
    """Base purchase schema"""
    listing_id: int
    amount: float
    payment_method: Optional[str] = None


class PurchaseCreate(PurchaseBase):
    """Purchase creation schema"""
    pass


class PurchaseUpdate(BaseModel):
    """Purchase update schema"""
    status: Optional[str] = None
    transaction_hash: Optional[str] = None


class Purchase(PurchaseBase):
    """Purchase response schema"""
    id: int
    user_id: int
    status: str
    transaction_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# User Activity schemas
class UserActivityBase(BaseModel):
    """Base user activity schema"""
    activity_type: str
    target_id: Optional[int] = None
    target_type: Optional[str] = None
    activity_data: Optional[str] = None


class UserActivityCreate(UserActivityBase):
    """User activity creation schema"""
    pass


class UserActivity(UserActivityBase):
    """User activity response schema"""
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Enhanced schemas with activity data
class UserActivitySummary(BaseModel):
    """Summary of user activity"""
    total_purchases: int
    total_spent: float
    recent_purchases: List[Purchase] = []
    recent_activities: List[UserActivity] = []
    favorite_categories: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)