"""SQLAlchemy ORM models for the application"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Float
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
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    marketplaces = relationship("Marketplace", back_populates="owner")
    listings = relationship("Listing", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")
    browsing_history = relationship("BrowsingHistory", back_populates="user")


class Marketplace(Base):
    """Marketplace model"""
    __tablename__ = "marketplaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

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
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    marketplace = relationship("Marketplace", back_populates="listings")
    user = relationship("User", back_populates="listings")
    purchases = relationship("Purchase", back_populates="listing")
    browsing_history = relationship("BrowsingHistory", back_populates="listing")


class Purchase(Base):
    """Purchase/Transaction model for tracking user purchases"""
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")  # pending, completed, failed, cancelled
    transaction_hash = Column(String(255), nullable=True)  # Solana transaction hash
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="purchases")
    listing = relationship("Listing", back_populates="purchases")


class BrowsingHistory(Base):
    """User browsing history model"""
    __tablename__ = "browsing_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    action = Column(String(50), nullable=False)  # view, search, favorite, share
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="browsing_history")
    listing = relationship("Listing", back_populates="browsing_history")
