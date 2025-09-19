"""SQLAlchemy ORM models for the application"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="buyer")  # buyer, seller, admin
    is_verified_seller = Column(Boolean, default=False)
    verification_nft_mint = Column(
        String(255), nullable=True
    )  # Solana NFT mint address
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    marketplaces = relationship("Marketplace", back_populates="owner")
    listings = relationship("Listing", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")
    orders_as_buyer = relationship(
        "Order", foreign_keys="Order.buyer_id", back_populates="buyer"
    )
    orders_as_seller = relationship(
        "Order", foreign_keys="Order.seller_id", back_populates="seller"
    )
    reviews_given = relationship(
        "UserReview", foreign_keys="UserReview.reviewer_id", back_populates="reviewer"
    )
    reviews_received = relationship(
        "UserReview",
        foreign_keys="UserReview.reviewed_user_id",
        back_populates="reviewed_user",
    )
    wishlist = relationship("UserWishlist", back_populates="user")


class Marketplace(Base):
    """Marketplace model"""

    __tablename__ = "marketplaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    owner = relationship("User", back_populates="marketplaces")
    listings = relationship("Listing", back_populates="marketplace")


class Listing(Base):
    """Listing model for goods and services"""

    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    marketplace_id = Column(Integer, ForeignKey("marketplaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    marketplace = relationship("Marketplace", back_populates="listings")
    user = relationship("User", back_populates="listings")
    purchases = relationship("Purchase", back_populates="listing")
    wishlist_items = relationship("UserWishlist", back_populates="listing")


class Purchase(Base):
    """Purchase/Transaction model for tracking user purchases"""

    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")  # pending, completed, cancelled
    payment_method = Column(String(50), nullable=True)  # solana, other
    transaction_hash = Column(String(255), nullable=True)  # Solana transaction hash
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="purchases")
    listing = relationship("Listing", back_populates="purchases")


class UserActivity(Base):
    """User activity model for tracking browsing and interaction history"""

    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(
        String(50), nullable=False
    )  # view, search, purchase, message
    target_id = Column(Integer, nullable=True)  # listing_id, marketplace_id, etc.
    target_type = Column(String(50), nullable=True)  # listing, marketplace, user
    activity_data = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="activities")


class Order(Base):
    """Order model for managing purchases with escrow"""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    quantity = Column(Integer, default=1)
    total_amount = Column(Float, nullable=False)
    delivery_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    escrow_tx_hash = Column(String(255), nullable=True)  # Solana escrow transaction
    status = Column(
        String(20), default="pending"
    )  # pending, paid, shipped, delivered, disputed, cancelled, completed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    buyer = relationship(
        "User", foreign_keys=[buyer_id], back_populates="orders_as_buyer"
    )
    seller = relationship(
        "User", foreign_keys=[seller_id], back_populates="orders_as_seller"
    )
    listing = relationship("Listing", back_populates="orders")
    review = relationship("UserReview", back_populates="order")


class MarketplaceRequest(Base):
    """Marketplace creation request model"""

    __tablename__ = "marketplace_requests"

    id = Column(Integer, primary_key=True, index=True)
    university_name = Column(String(255), nullable=False)
    university_domain = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    smart_contract_tx_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    requester = relationship("User", back_populates="marketplace_requests")


# Add marketplace_requests relationship to User
User.marketplace_requests = relationship(
    "MarketplaceRequest", back_populates="requester"
)

# Add orders relationship to Listing
Listing.orders = relationship("Order", back_populates="listing")


class UserReview(Base):
    """User review model for rating and reviewing other users"""

    __tablename__ = "user_reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    order_id = Column(
        Integer, ForeignKey("orders.id"), nullable=True
    )  # Optional: link to specific order
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    reviewer = relationship(
        "User", foreign_keys=[reviewer_id], back_populates="reviews_given"
    )
    reviewed_user = relationship(
        "User", foreign_keys=[reviewed_user_id], back_populates="reviews_received"
    )
    order = relationship("Order", back_populates="review")


class UserWishlist(Base):
    """User wishlist model for saving favorite listings"""

    __tablename__ = "user_wishlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="wishlist")
    listing = relationship("Listing", back_populates="wishlist_items")

    # Ensure unique user-listing combination
    __table_args__ = ({"extend_existing": True},)
