"""CRUD operations for database models"""

from typing import Optional, List

from sqlalchemy.orm import Session

from . import models, schemas
from .auth import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(
    db: Session, username: str, password: str
) -> Optional[models.User]:
    """Authenticate a user"""
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_marketplace(
    db: Session, marketplace: schemas.MarketplaceCreate, user_id: int
) -> models.Marketplace:
    """Create a new marketplace"""
    db_marketplace = models.Marketplace(
        name=marketplace.name,
        description=marketplace.description,
        created_by=user_id,
    )
    db.add(db_marketplace)
    db.commit()
    db.refresh(db_marketplace)
    return db_marketplace


def get_marketplace(db: Session, marketplace_id: int) -> Optional[models.Marketplace]:
    """Get marketplace by ID"""
    return (
        db.query(models.Marketplace)
        .filter(models.Marketplace.id == marketplace_id)
        .first()
    )


def create_listing(
    db: Session, listing: schemas.ListingCreate, user_id: int
) -> models.Listing:
    """Create a new listing"""
    db_listing = models.Listing(
        title=listing.title,
        description=listing.description,
        price=listing.price,
        category=listing.category,
        marketplace_id=listing.marketplace_id,
        user_id=user_id,
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def get_listing(db: Session, listing_id: int) -> Optional[models.Listing]:
    """Get listing by ID"""
    return db.query(models.Listing).filter(models.Listing.id == listing_id).first()


def get_listings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    marketplace_id: Optional[int] = None,
    category: Optional[str] = None,
) -> List[models.Listing]:
    """Get listings with optional filtering by marketplace_id and category"""
    query = db.query(models.Listing).filter(models.Listing.is_active)

    if marketplace_id is not None:
        query = query.filter(models.Listing.marketplace_id == marketplace_id)

    if category is not None:
        query = query.filter(models.Listing.category == category)

    return query.offset(skip).limit(limit).all()


def update_listing(
    db: Session, listing_id: int, listing_update: schemas.ListingUpdate
) -> Optional[models.Listing]:
    """Update a listing"""
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return None

    # Update only provided fields
    update_data = listing_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_listing, field, value)

    db.commit()
    db.refresh(db_listing)
    return db_listing


def delete_listing(db: Session, listing_id: int) -> bool:
    """Delete a listing (soft delete by setting is_active to False)"""
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return False

    db_listing.is_active = False
    db.commit()
    return True
