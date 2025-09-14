"""CRUD operations for database models"""

from typing import Optional, List
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import func

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


def create_purchase(
    db: Session, purchase: schemas.PurchaseCreate, user_id: int
) -> models.Purchase:
    """Create a new purchase"""
    db_purchase = models.Purchase(
        user_id=user_id,
        listing_id=purchase.listing_id,
        amount=purchase.amount,
        payment_method=purchase.payment_method,
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


def get_purchase(db: Session, purchase_id: int) -> Optional[models.Purchase]:
    """Get purchase by ID"""
    return db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()


def get_user_purchases(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Purchase]:
    """Get all purchases for a user"""
    return (
        db.query(models.Purchase)
        .filter(models.Purchase.user_id == user_id)
        .order_by(models.Purchase.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_user_activity(
    db: Session, activity: schemas.UserActivityCreate, user_id: int
) -> models.UserActivity:
    """Create a new user activity record"""
    db_activity = models.UserActivity(
        user_id=user_id,
        activity_type=activity.activity_type,
        target_id=activity.target_id,
        target_type=activity.target_type,
        activity_data=activity.activity_data,
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def get_user_activities(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.UserActivity]:
    """Get all activities for a user"""
    return (
        db.query(models.UserActivity)
        .filter(models.UserActivity.user_id == user_id)
        .order_by(models.UserActivity.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_activity_summary(db: Session, user_id: int) -> dict:
    """Get comprehensive user activity summary for agent recommendations"""
    # Get user purchases
    purchases = get_user_purchases(db, user_id, limit=50)
    
    # Get user activities
    activities = get_user_activities(db, user_id, limit=100)
    
    # Calculate summary statistics
    total_purchases = len(purchases)
    total_spent = sum(p.amount for p in purchases if p.status == "completed")
    
    # Get favorite categories from purchases
    if purchases:
        # Get listings for completed purchases
        completed_purchases = [p for p in purchases if p.status == "completed"]
        if completed_purchases:
            listing_ids = [p.listing_id for p in completed_purchases]
            listings = (
                db.query(models.Listing)
                .filter(models.Listing.id.in_(listing_ids))
                .all()
            )
            categories = [l.category for l in listings if l.category]
            category_counts = Counter(categories)
            favorite_categories = [cat for cat, count in category_counts.most_common(5)]
        else:
            favorite_categories = []
    else:
        favorite_categories = []
    
    # Get recent activity summary
    recent_views = [a for a in activities if a.activity_type == "view"][:10]
    recent_searches = [a for a in activities if a.activity_type == "search"][:10]
    
    return {
        "user_id": user_id,
        "total_purchases": total_purchases,
        "total_spent": total_spent,
        "recent_purchases": purchases[:10],
        "recent_activities": activities[:20],
        "favorite_categories": favorite_categories,
        "recent_views": recent_views,
        "recent_searches": recent_searches,
    }
