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
    sent_messages = relationship(
        "Message", foreign_keys="Message.sender_id", back_populates="sender"
    )
    received_messages = relationship(
        "Message", foreign_keys="Message.recipient_id", back_populates="recipient"
    )
    points = relationship("UserPoints", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")
    points_transactions = relationship("PointsTransaction", back_populates="user")
    leaderboard_entries = relationship("CampusLeaderboard", back_populates="user")
    bill_payments = relationship("BillPayment", back_populates="user")
    wallet_transactions = relationship("WalletTransaction", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


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
    leaderboard = relationship("CampusLeaderboard", back_populates="marketplace")


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
    images = relationship("ListingImage", back_populates="listing")
    messages = relationship("Message", back_populates="listing")


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
    delivery_code = relationship("DeliveryCode", back_populates="order")


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


class ListingImage(Base):
    """Listing image model for storing image metadata"""

    __tablename__ = "listing_images"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    is_primary = Column(Boolean, default=False)  # Primary image for the listing
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    listing = relationship("Listing", back_populates="images")


class Message(Base):
    """Direct message model for user communication"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(
        Integer, ForeignKey("listings.id"), nullable=True
    )  # Optional: linked to specific listing
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sender = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    recipient = relationship(
        "User", foreign_keys=[recipient_id], back_populates="received_messages"
    )
    listing = relationship("Listing", back_populates="messages")


class UserPoints(Base):
    """User points and gamification model"""

    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    total_points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="points")


class UserBadge(Base):
    """User badges model"""

    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_name = Column(String(100), nullable=False)
    badge_description = Column(Text, nullable=True)
    badge_type = Column(String(50), nullable=False)  # achievement, milestone, special
    earned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    points_awarded = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="badges")


class PointsTransaction(Base):
    """Points transaction history model"""

    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points_change = Column(
        Integer, nullable=False
    )  # Positive for earned, negative for spent
    transaction_type = Column(
        String(50), nullable=False
    )  # purchase, sale, review, badge, etc.
    description = Column(Text, nullable=True)
    related_entity_id = Column(Integer, nullable=True)  # order_id, listing_id, etc.
    related_entity_type = Column(
        String(50), nullable=True
    )  # order, listing, review, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="points_transactions")


class CampusLeaderboard(Base):
    """Campus leaderboard model"""

    __tablename__ = "campus_leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    marketplace_id = Column(Integer, ForeignKey("marketplaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rank = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    badges_count = Column(Integer, default=0)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    marketplace = relationship("Marketplace", back_populates="leaderboard")
    user = relationship("User", back_populates="leaderboard_entries")


class BillPayment(Base):
    """Bill payment model"""

    __tablename__ = "bill_payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bill_type = Column(String(50), nullable=False)  # tuition, housing, meal_plan, etc.
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")  # pending, paid, overdue, cancelled
    payment_method = Column(String(50), nullable=True)  # solana, card, etc.
    transaction_hash = Column(String(255), nullable=True)  # Solana transaction hash
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="bill_payments")


class WalletTransaction(Base):
    """Wallet transaction model"""

    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(
        String(50), nullable=False
    )  # deposit, withdrawal, payment, refund
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    transaction_hash = Column(String(255), nullable=True)  # Solana transaction hash
    status = Column(
        String(20), default="pending"
    )  # pending, completed, failed, cancelled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="wallet_transactions")


class DeliveryCode(Base):
    """Delivery code model for order confirmation"""

    __tablename__ = "delivery_codes"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    code = Column(String(10), nullable=False, unique=True)  # 6-digit code
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = relationship("Order", back_populates="delivery_code")


class Notification(Base):
    """Notification model"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(
        String(50), nullable=False
    )  # order_update, payment, delivery, etc.
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    related_entity_id = Column(Integer, nullable=True)  # order_id, listing_id, etc.
    related_entity_type = Column(String(50), nullable=True)  # order, listing, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="notifications")


class FraudReport(Base):
    """Fraud detection report model"""

    __tablename__ = "fraud_reports"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # user, listing, payment
    entity_id = Column(Integer, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, medium, high
    flagged_reasons = Column(
        Text, nullable=True
    )  # JSON string for SQLite compatibility
    detection_method = Column(
        String(50), nullable=False
    )  # ai_agent, pattern_analysis, manual
    confidence = Column(Float, nullable=False)
    status = Column(
        String(20), default="pending"
    )  # pending, reviewed, false_positive, confirmed_fraud
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
