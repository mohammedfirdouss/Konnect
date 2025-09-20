"""Pydantic schemas for API validation and serialization"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


from uuid import UUID


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


class User(UserBase):
    """User response schema"""

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Token schemas
class Token(BaseModel):
    """Token response schema"""

    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


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


# Recommendation schemas
class RecommendationResponse(BaseModel):
    """Response schema for user recommendations"""

    user_id: int
    listing_ids: List[int]
    cached_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


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


# Order/Escrow schemas
class OrderBase(BaseModel):
    """Base order schema"""

    listing_id: int
    quantity: int = 1
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema"""

    pass


class OrderUpdate(BaseModel):
    """Order update schema"""

    status: Optional[str] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class Order(OrderBase):
    """Order response schema"""

    id: int
    buyer_id: int
    seller_id: int
    total_amount: float
    escrow_tx_hash: Optional[str] = None
    status: str  # pending, paid, shipped, delivered, disputed, cancelled, completed
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Admin schemas
class SellerVerificationRequest(BaseModel):
    """Seller verification request"""

    seller_id: int


class SellerVerificationResponse(BaseModel):
    """Seller verification response"""

    seller_id: int
    verified: bool
    nft_mint_tx_hash: Optional[str] = None
    verified_at: Optional[datetime] = None


class PendingSeller(BaseModel):
    """Pending seller for verification"""

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    total_listings: int

    model_config = ConfigDict(from_attributes=True)


class AdminStats(BaseModel):
    """Admin dashboard statistics"""

    total_users: int
    total_sellers: int
    verified_sellers: int
    pending_sellers: int
    total_listings: int
    active_listings: int
    total_orders: int
    disputed_orders: int


# AI Insights schemas
class SellerInsights(BaseModel):
    """Seller insights response"""

    seller_id: int
    total_sales: int
    total_revenue: float
    average_order_value: float
    top_products: List[dict] = []
    sales_trend: List[dict] = []
    customer_satisfaction: float
    recommendations: List[str] = []


class AIRecommendation(BaseModel):
    """AI-powered recommendation"""

    listing_id: int
    title: str
    price: float
    category: Optional[str] = None
    confidence_score: float
    reason: str


class AIRecommendationsResponse(BaseModel):
    """AI recommendations response"""

    user_id: int
    recommendations: List[AIRecommendation] = []
    generated_at: datetime


# Product search schemas
class ProductSearchFilters(BaseModel):
    """Product search filters"""

    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    marketplace_id: Optional[int] = None
    verified_sellers_only: bool = False
    sort_by: Optional[str] = (
        "relevance"  # relevance, price_asc, price_desc, newest, oldest
    )


class ProductSearchResult(BaseModel):
    """Product search result"""

    id: int
    title: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    marketplace_id: int
    marketplace_name: str
    seller_id: int
    seller_username: str
    seller_verified: bool
    created_at: datetime
    relevance_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ProductSearchResponse(BaseModel):
    """Product search response"""

    results: List[ProductSearchResult] = []
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: ProductSearchFilters


# Marketplace request schemas
class MarketplaceRequest(BaseModel):
    """Marketplace creation request"""

    university_name: str
    university_domain: str
    contact_email: str
    description: Optional[str] = None


class MarketplaceRequestResponse(BaseModel):
    """Marketplace request response"""

    id: int
    university_name: str
    status: str  # pending, approved, rejected
    requested_by: int
    created_at: datetime
    smart_contract_tx_hash: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# User Review schemas
class ReviewBase(BaseModel):
    """Base review schema"""

    rating: int  # 1-5 stars
    comment: Optional[str] = None
    order_id: Optional[int] = None


class ReviewCreate(ReviewBase):
    """Review creation schema"""

    reviewed_user_id: int


class ReviewUpdate(BaseModel):
    """Review update schema"""

    rating: Optional[int] = None
    comment: Optional[str] = None


class Review(ReviewBase):
    """Review response schema"""

    id: int
    reviewer_id: int
    reviewed_user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewWithDetails(Review):
    """Review schema with reviewer details"""

    reviewer_username: str
    reviewer_full_name: Optional[str] = None


class UserReviewSummary(BaseModel):
    """User review summary"""

    user_id: int
    total_reviews: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, ...}


# User Wishlist schemas
class WishlistItem(BaseModel):
    """Wishlist item response schema"""

    id: int
    listing_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WishlistItemWithDetails(WishlistItem):
    """Wishlist item with listing details"""

    listing_title: str
    listing_price: float
    listing_category: Optional[str] = None
    listing_description: Optional[str] = None
    seller_username: str
    marketplace_name: str


class WishlistResponse(BaseModel):
    """Wishlist response schema"""

    items: List[WishlistItemWithDetails] = []
    total_count: int


# Listing Image schemas
class ListingImageBase(BaseModel):
    """Base listing image schema"""

    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    is_primary: bool = False


class ListingImageCreate(BaseModel):
    """Listing image creation schema"""

    is_primary: bool = False


class ListingImage(ListingImageBase):
    """Listing image response schema"""

    id: int
    listing_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ListingImageUploadResponse(BaseModel):
    """Response schema for image upload"""

    id: int
    listing_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    is_primary: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Message schemas
class MessageBase(BaseModel):
    """Base message schema"""

    recipient_id: int
    subject: Optional[str] = None
    content: str
    listing_id: Optional[int] = None


class MessageCreate(MessageBase):
    """Message creation schema"""

    pass


class MessageUpdate(BaseModel):
    """Message update schema"""

    is_read: Optional[bool] = None


class Message(MessageBase):
    """Message response schema"""

    id: int
    sender_id: int
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageWithDetails(Message):
    """Message schema with sender and recipient details"""

    sender_username: str
    sender_full_name: Optional[str] = None
    recipient_username: str
    recipient_full_name: Optional[str] = None
    listing_title: Optional[str] = None


class MessageThread(BaseModel):
    """Message thread schema"""

    other_user_id: int
    other_user_username: str
    other_user_full_name: Optional[str] = None
    last_message: Optional[Message] = None
    unread_count: int = 0
    total_messages: int = 0


class MessageThreadResponse(BaseModel):
    """Response schema for message threads"""

    threads: List[MessageThread] = []
    total_count: int


class MessageHistoryResponse(BaseModel):
    """Response schema for message history"""

    messages: List[MessageWithDetails] = []
    other_user_id: int
    other_user_username: str
    other_user_full_name: Optional[str] = None
    total_count: int


# AI-Powered Features schemas
class AISearchRequest(BaseModel):
    """Request schema for AI semantic search"""

    query: str
    max_results: int = 20
    include_explanation: bool = True


class AISearchResult(BaseModel):
    """AI search result with relevance score and explanation"""

    listing_id: int
    title: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    seller_username: str
    marketplace_name: str
    relevance_score: float
    explanation: Optional[str] = None
    matched_keywords: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class AISearchResponse(BaseModel):
    """Response schema for AI semantic search"""

    query: str
    results: List[AISearchResult] = []
    total_found: int
    search_time_ms: int
    explanation: Optional[str] = None


class PriceSuggestionRequest(BaseModel):
    """Request schema for AI price suggestion"""

    title: str
    category: Optional[str] = None
    condition: Optional[str] = None  # new, good, fair, poor
    brand: Optional[str] = None
    additional_details: Optional[str] = None


class PriceSuggestionResponse(BaseModel):
    """Response schema for AI price suggestion"""

    suggested_price_range: dict  # {"min": float, "max": float, "recommended": float}
    market_analysis: (
        dict  # {"average_price": float, "price_trend": str, "competition_level": str}
    )
    reasoning: str
    similar_listings: List[dict] = []  # List of similar listings with prices
    confidence_score: float  # 0.0 to 1.0


class DescriptionGenerationRequest(BaseModel):
    """Request schema for AI description generation"""

    title: str
    category: Optional[str] = None
    condition: Optional[str] = None
    brand: Optional[str] = None
    key_features: List[str] = []
    target_audience: Optional[str] = None  # students, general, etc.
    tone: str = "professional"  # professional, casual, friendly


class DescriptionGenerationResponse(BaseModel):
    """Response schema for AI description generation"""

    generated_description: str
    alternative_descriptions: List[str] = []
    suggested_keywords: List[str] = []
    seo_score: float  # 0.0 to 1.0
    readability_score: float  # 0.0 to 1.0


class FraudDetectionReport(BaseModel):
    """Fraud detection report schema"""

    id: int
    entity_type: str  # "user" or "listing"
    entity_id: int
    risk_score: float  # 0.0 to 1.0
    risk_level: str  # "low", "medium", "high", "critical"
    flagged_reasons: List[str] = []
    detection_method: str
    confidence: float  # 0.0 to 1.0
    created_at: datetime
    status: str  # "pending", "investigated", "resolved", "false_positive"
    admin_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FraudDetectionSummary(BaseModel):
    """Summary of fraud detection reports"""

    total_reports: int
    high_risk_reports: int
    medium_risk_reports: int
    pending_investigation: int
    recent_activity: List[FraudDetectionReport] = []
    risk_trends: dict = {}  # {"user_fraud": int, "listing_fraud": int, "payment_fraud": int}


class FraudDetectionResponse(BaseModel):
    """Response schema for fraud detection reports"""

    reports: List[FraudDetectionReport] = []
    summary: FraudDetectionSummary
    total_count: int
    page: int
    page_size: int
