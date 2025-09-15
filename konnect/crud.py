"""CRUD operations for database models"""

from collections import Counter
from typing import List, Optional

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
            categories = [listing.category for listing in listings if listing.category]
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


# Marketplace CRUD functions
def get_marketplaces(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Marketplace]:
    """Get all marketplaces"""
    return (
        db.query(models.Marketplace)
        .filter(models.Marketplace.is_active)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_marketplace_request(
    db: Session, request: schemas.MarketplaceRequest, user_id: int
) -> models.MarketplaceRequest:
    """Create a marketplace creation request"""
    db_request = models.MarketplaceRequest(
        university_name=request.university_name,
        university_domain=request.university_domain,
        contact_email=request.contact_email,
        description=request.description,
        requested_by=user_id,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def get_marketplace_request(
    db: Session, request_id: int
) -> Optional[models.MarketplaceRequest]:
    """Get marketplace request by ID"""
    return (
        db.query(models.MarketplaceRequest)
        .filter(models.MarketplaceRequest.id == request_id)
        .first()
    )


def get_pending_marketplace_requests(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.MarketplaceRequest]:
    """Get pending marketplace requests"""
    return (
        db.query(models.MarketplaceRequest)
        .filter(models.MarketplaceRequest.status == "pending")
        .offset(skip)
        .limit(limit)
        .all()
    )


def approve_marketplace_request(
    db: Session, request_id: int, contract_tx_hash: str
) -> models.Marketplace:
    """Approve marketplace request and create marketplace"""
    request = get_marketplace_request(db, request_id)
    if not request:
        return None

    # Update request status
    request.status = "approved"
    request.smart_contract_tx_hash = contract_tx_hash

    # Create the marketplace
    marketplace = models.Marketplace(
        name=request.university_name,
        description=request.description,
        created_by=request.requested_by,
    )
    db.add(marketplace)

    db.commit()
    db.refresh(marketplace)
    return marketplace


def reject_marketplace_request(
    db: Session, request_id: int
) -> models.MarketplaceRequest:
    """Reject marketplace request"""
    request = get_marketplace_request(db, request_id)
    if request:
        request.status = "rejected"
        db.commit()
        db.refresh(request)
    return request


# Order CRUD functions
def create_order(
    db: Session,
    order: schemas.OrderCreate,
    buyer_id: int,
    seller_id: int,
    total_amount: float,
    escrow_tx_hash: str,
) -> models.Order:
    """Create a new order"""
    db_order = models.Order(
        buyer_id=buyer_id,
        seller_id=seller_id,
        listing_id=order.listing_id,
        quantity=order.quantity,
        total_amount=total_amount,
        delivery_address=order.delivery_address,
        notes=order.notes,
        escrow_tx_hash=escrow_tx_hash,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    """Get order by ID"""
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def update_order_status(
    db: Session, order_id: int, status: str
) -> Optional[models.Order]:
    """Update order status"""
    order = get_order(db, order_id)
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order


# Admin CRUD functions
def get_pending_sellers(
    db: Session, skip: int = 0, limit: int = 100
) -> List[schemas.PendingSeller]:
    """Get sellers awaiting verification"""
    sellers = (
        db.query(models.User)
        .filter(models.User.role == "seller")
        .filter(not models.User.is_verified_seller)
        .filter(models.User.is_active)
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for seller in sellers:
        # Count total listings for this seller
        total_listings = (
            db.query(models.Listing)
            .filter(models.Listing.user_id == seller.id, models.Listing.is_active)
            .count()
        )

        result.append(
            schemas.PendingSeller(
                id=seller.id,
                username=seller.username,
                email=seller.email,
                full_name=seller.full_name,
                created_at=seller.created_at,
                total_listings=total_listings,
            )
        )

    return result


def verify_seller(db: Session, seller_id: int, nft_mint_tx_hash: str) -> models.User:
    """Verify a seller and set NFT mint hash"""
    seller = get_user(db, seller_id)
    if seller and seller.role == "seller":
        from datetime import datetime, timezone

        seller.is_verified_seller = True
        seller.verification_nft_mint = nft_mint_tx_hash
        seller.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(seller)
    return seller


def force_delete_listing(db: Session, listing_id: int) -> bool:
    """Force delete a listing (admin only)"""
    listing = get_listing(db, listing_id)
    if listing:
        db.delete(listing)
        db.commit()
        return True
    return False


def get_admin_stats(db: Session) -> dict:
    """Get admin dashboard statistics"""
    total_users = db.query(models.User).filter(models.User.is_active).count()
    total_sellers = (
        db.query(models.User)
        .filter(models.User.role == "seller", models.User.is_active)
        .count()
    )
    verified_sellers = (
        db.query(models.User)
        .filter(models.User.is_verified_seller, models.User.is_active)
        .count()
    )
    pending_sellers = total_sellers - verified_sellers
    total_listings = db.query(models.Listing).filter(models.Listing.is_active).count()
    active_listings = total_listings  # All active listings are considered active
    total_orders = db.query(models.Order).count()
    disputed_orders = (
        db.query(models.Order).filter(models.Order.status == "disputed").count()
    )

    return {
        "total_users": total_users,
        "total_sellers": total_sellers,
        "verified_sellers": verified_sellers,
        "pending_sellers": pending_sellers,
        "total_listings": total_listings,
        "active_listings": active_listings,
        "total_orders": total_orders,
        "disputed_orders": disputed_orders,
    }


# Product search CRUD functions
def search_products(
    db: Session, filters: schemas.ProductSearchFilters, offset: int = 0, limit: int = 20
) -> dict:
    """Advanced product search with filters"""
    query = db.query(models.Listing).filter(models.Listing.is_active)

    # Apply filters
    if filters.query:
        search_term = f"%{filters.query}%"
        query = query.filter(
            (models.Listing.title.ilike(search_term))
            | (models.Listing.description.ilike(search_term))
        )

    if filters.category:
        query = query.filter(models.Listing.category == filters.category)

    if filters.min_price is not None:
        query = query.filter(models.Listing.price >= filters.min_price)

    if filters.max_price is not None:
        query = query.filter(models.Listing.price <= filters.max_price)

    if filters.marketplace_id:
        query = query.filter(models.Listing.marketplace_id == filters.marketplace_id)

    if filters.verified_sellers_only:
        query = query.join(models.User).filter(models.User.is_verified_seller)

    # Apply sorting
    if filters.sort_by == "price_asc":
        query = query.order_by(models.Listing.price.asc())
    elif filters.sort_by == "price_desc":
        query = query.order_by(models.Listing.price.desc())
    elif filters.sort_by == "newest":
        query = query.order_by(models.Listing.created_at.desc())
    elif filters.sort_by == "oldest":
        query = query.order_by(models.Listing.created_at.asc())
    else:  # relevance (default)
        query = query.order_by(models.Listing.created_at.desc())  # Simple relevance

    # Get total count
    total_count = query.count()

    # Apply pagination and get results
    results = query.offset(offset).limit(limit).all()

    # Format results
    formatted_results = []
    for listing in results:
        seller = listing.user
        marketplace = listing.marketplace

        formatted_results.append(
            {
                "id": listing.id,
                "title": listing.title,
                "description": listing.description,
                "price": listing.price,
                "category": listing.category,
                "marketplace_id": listing.marketplace_id,
                "marketplace_name": marketplace.name if marketplace else "Unknown",
                "seller_id": listing.user_id,
                "seller_username": seller.username,
                "seller_verified": seller.is_verified_seller,
                "created_at": listing.created_at,
                "relevance_score": None,  # Could implement text similarity scoring
            }
        )

    return {
        "results": formatted_results,
        "total_count": total_count,
    }


def get_all_categories(db: Session) -> List[str]:
    """Get all unique product categories"""
    categories = (
        db.query(models.Listing.category)
        .filter(models.Listing.category.isnot(None))
        .filter(models.Listing.is_active)
        .distinct()
        .all()
    )
    return [cat[0] for cat in categories if cat[0]]


def get_trending_products(db: Session, limit: int = 10) -> List[models.Listing]:
    """Get trending products based on recent activity"""
    # Simple trending logic: recent listings with most activity
    # In production, this could be based on views, purchases, etc.
    return (
        db.query(models.Listing)
        .filter(models.Listing.is_active)
        .order_by(models.Listing.created_at.desc())
        .limit(limit)
        .all()
    )


def get_related_products(
    db: Session, product_id: int, limit: int = 5
) -> List[models.Listing]:
    """Get products related to a specific product"""
    # Get the original product
    product = get_listing(db, product_id)
    if not product:
        return []

    # Find products in same category and similar price range
    related = (
        db.query(models.Listing)
        .filter(models.Listing.id != product_id)
        .filter(models.Listing.is_active)
        .filter(models.Listing.category == product.category)
        .filter(models.Listing.price.between(product.price * 0.7, product.price * 1.3))
        .limit(limit)
        .all()
    )

    return related


def get_seller_stats(db: Session, seller_id: int) -> dict:
    """Get statistics for a seller"""
    # Get seller's listings
    listings = (
        db.query(models.Listing)
        .filter(models.Listing.user_id == seller_id)
        .filter(models.Listing.is_active)
        .all()
    )

    # Get seller's orders (as seller)
    orders = db.query(models.Order).filter(models.Order.seller_id == seller_id).all()

    total_sales = len([o for o in orders if o.status == "completed"])
    total_revenue = sum(o.total_amount for o in orders if o.status == "completed")
    avg_order_value = total_revenue / total_sales if total_sales > 0 else 0

    # Get top products
    top_products = []
    if listings:
        for listing in listings[:5]:  # Top 5 listings
            order_count = len(
                [
                    o
                    for o in orders
                    if o.listing_id == listing.id and o.status == "completed"
                ]
            )
            if order_count > 0:
                top_products.append(
                    {
                        "id": listing.id,
                        "title": listing.title,
                        "orders": order_count,
                        "revenue": sum(
                            o.total_amount
                            for o in orders
                            if o.listing_id == listing.id and o.status == "completed"
                        ),
                    }
                )

    return {
        "total_orders": len(orders),
        "total_revenue": total_revenue,
        "avg_order_value": avg_order_value,
        "top_products": top_products,
    }
