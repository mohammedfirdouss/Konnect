"""CRUD operations for database models"""

from collections import Counter
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


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


# User Review CRUD functions
def create_user_review(
    db: Session, review: schemas.ReviewCreate, reviewer_id: int
) -> models.UserReview:
    """Create a new user review"""
    # Check if reviewer has already reviewed this user
    existing_review = (
        db.query(models.UserReview)
        .filter(
            models.UserReview.reviewer_id == reviewer_id,
            models.UserReview.reviewed_user_id == review.reviewed_user_id,
        )
        .first()
    )

    if existing_review:
        raise ValueError("You have already reviewed this user")

    # Validate rating
    if not (1 <= review.rating <= 5):
        raise ValueError("Rating must be between 1 and 5")

    db_review = models.UserReview(
        reviewer_id=reviewer_id,
        reviewed_user_id=review.reviewed_user_id,
        rating=review.rating,
        comment=review.comment,
        order_id=review.order_id,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def get_user_reviews(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.UserReview]:
    """Get all reviews for a specific user"""
    return (
        db.query(models.UserReview)
        .filter(models.UserReview.reviewed_user_id == user_id)
        .order_by(models.UserReview.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_review_summary(db: Session, user_id: int) -> dict:
    """Get review summary for a user"""
    reviews = (
        db.query(models.UserReview)
        .filter(models.UserReview.reviewed_user_id == user_id)
        .all()
    )

    if not reviews:
        return {
            "user_id": user_id,
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }

    total_reviews = len(reviews)
    average_rating = sum(r.rating for r in reviews) / total_reviews

    # Count rating distribution
    rating_counts = Counter(r.rating for r in reviews)
    rating_distribution = {i: rating_counts.get(i, 0) for i in range(1, 6)}

    return {
        "user_id": user_id,
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 2),
        "rating_distribution": rating_distribution,
    }


def update_user_review(
    db: Session, review_id: int, review_update: schemas.ReviewUpdate, reviewer_id: int
) -> Optional[models.UserReview]:
    """Update a user review (only by the reviewer)"""
    db_review = (
        db.query(models.UserReview)
        .filter(
            models.UserReview.id == review_id,
            models.UserReview.reviewer_id == reviewer_id,
        )
        .first()
    )

    if not db_review:
        return None

    # Update only provided fields
    update_data = review_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "rating" and not (1 <= value <= 5):
            raise ValueError("Rating must be between 1 and 5")
        setattr(db_review, field, value)

    db.commit()
    db.refresh(db_review)
    return db_review


def delete_user_review(db: Session, review_id: int, reviewer_id: int) -> bool:
    """Delete a user review (only by the reviewer)"""
    db_review = (
        db.query(models.UserReview)
        .filter(
            models.UserReview.id == review_id,
            models.UserReview.reviewer_id == reviewer_id,
        )
        .first()
    )

    if not db_review:
        return False

    db.delete(db_review)
    db.commit()
    return True


# User Wishlist CRUD functions
def add_to_wishlist(db: Session, user_id: int, listing_id: int) -> models.UserWishlist:
    """Add a listing to user's wishlist"""
    # Check if already in wishlist
    existing_item = (
        db.query(models.UserWishlist)
        .filter(
            models.UserWishlist.user_id == user_id,
            models.UserWishlist.listing_id == listing_id,
        )
        .first()
    )

    if existing_item:
        raise ValueError("Listing is already in your wishlist")

    # Verify listing exists and is active
    listing = get_listing(db, listing_id)
    if not listing or not listing.is_active:
        raise ValueError("Listing not found or inactive")

    db_wishlist_item = models.UserWishlist(user_id=user_id, listing_id=listing_id)
    db.add(db_wishlist_item)
    db.commit()
    db.refresh(db_wishlist_item)
    return db_wishlist_item


def remove_from_wishlist(db: Session, user_id: int, listing_id: int) -> bool:
    """Remove a listing from user's wishlist"""
    db_wishlist_item = (
        db.query(models.UserWishlist)
        .filter(
            models.UserWishlist.user_id == user_id,
            models.UserWishlist.listing_id == listing_id,
        )
        .first()
    )

    if not db_wishlist_item:
        return False

    db.delete(db_wishlist_item)
    db.commit()
    return True


def get_user_wishlist(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.UserWishlist]:
    """Get user's wishlist"""
    return (
        db.query(models.UserWishlist)
        .filter(models.UserWishlist.user_id == user_id)
        .order_by(models.UserWishlist.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_wishlist_with_details(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[dict]:
    """Get user's wishlist with listing details"""
    wishlist_items = (
        db.query(models.UserWishlist, models.Listing, models.User, models.Marketplace)
        .join(models.Listing, models.UserWishlist.listing_id == models.Listing.id)
        .join(models.User, models.Listing.user_id == models.User.id)
        .join(
            models.Marketplace, models.Listing.marketplace_id == models.Marketplace.id
        )
        .filter(models.UserWishlist.user_id == user_id)
        .filter(models.Listing.is_active)
        .order_by(models.UserWishlist.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for wishlist_item, listing, seller, marketplace in wishlist_items:
        result.append(
            {
                "id": wishlist_item.id,
                "listing_id": listing.id,
                "created_at": wishlist_item.created_at,
                "listing_title": listing.title,
                "listing_price": listing.price,
                "listing_category": listing.category,
                "listing_description": listing.description,
                "seller_username": seller.username,
                "marketplace_name": marketplace.name,
            }
        )

    return result


def is_in_wishlist(db: Session, user_id: int, listing_id: int) -> bool:
    """Check if a listing is in user's wishlist"""
    return (
        db.query(models.UserWishlist)
        .filter(
            models.UserWishlist.user_id == user_id,
            models.UserWishlist.listing_id == listing_id,
        )
        .first()
        is not None
    )


# Listing Image CRUD functions
def create_listing_image(
    db: Session,
    listing_id: int,
    filename: str,
    original_filename: str,
    file_path: str,
    file_size: int,
    mime_type: str,
    is_primary: bool = False,
) -> models.ListingImage:
    """Create a new listing image"""
    # If this is set as primary, unset other primary images for this listing
    if is_primary:
        db.query(models.ListingImage).filter(
            models.ListingImage.listing_id == listing_id,
            models.ListingImage.is_primary,
        ).update({"is_primary": False})

    db_image = models.ListingImage(
        listing_id=listing_id,
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        is_primary=is_primary,
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_listing_images(db: Session, listing_id: int) -> List[models.ListingImage]:
    """Get all images for a listing"""
    return (
        db.query(models.ListingImage)
        .filter(models.ListingImage.listing_id == listing_id)
        .order_by(
            models.ListingImage.is_primary.desc(), models.ListingImage.created_at.asc()
        )
        .all()
    )


def get_listing_image(db: Session, image_id: int) -> Optional[models.ListingImage]:
    """Get a specific listing image"""
    return (
        db.query(models.ListingImage).filter(models.ListingImage.id == image_id).first()
    )


def delete_listing_image(db: Session, image_id: int, listing_id: int) -> bool:
    """Delete a listing image"""
    db_image = (
        db.query(models.ListingImage)
        .filter(
            models.ListingImage.id == image_id,
            models.ListingImage.listing_id == listing_id,
        )
        .first()
    )

    if not db_image:
        return False

    db.delete(db_image)
    db.commit()
    return True


def set_primary_image(db: Session, image_id: int, listing_id: int) -> bool:
    """Set an image as the primary image for a listing"""
    # First, unset all primary images for this listing
    db.query(models.ListingImage).filter(
        models.ListingImage.listing_id == listing_id,
        models.ListingImage.is_primary,
    ).update({"is_primary": False})

    # Set the specified image as primary
    db_image = (
        db.query(models.ListingImage)
        .filter(
            models.ListingImage.id == image_id,
            models.ListingImage.listing_id == listing_id,
        )
        .first()
    )

    if not db_image:
        return False

    db_image.is_primary = True
    db.commit()
    db.refresh(db_image)
    return True


# Message CRUD functions
def create_message(
    db: Session, message: schemas.MessageCreate, sender_id: int
) -> models.Message:
    """Create a new message"""
    db_message = models.Message(
        sender_id=sender_id,
        recipient_id=message.recipient_id,
        listing_id=message.listing_id,
        subject=message.subject,
        content=message.content,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_message(db: Session, message_id: int) -> Optional[models.Message]:
    """Get a specific message"""
    return db.query(models.Message).filter(models.Message.id == message_id).first()


def get_message_threads(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[dict]:
    """Get all message threads for a user"""
    # Get all unique users that the current user has exchanged messages with
    sent_messages = (
        db.query(models.Message.recipient_id)
        .filter(models.Message.sender_id == user_id)
        .distinct()
        .all()
    )

    received_messages = (
        db.query(models.Message.sender_id)
        .filter(models.Message.recipient_id == user_id)
        .distinct()
        .all()
    )

    # Combine and get unique user IDs
    all_user_ids = set()
    for msg in sent_messages:
        all_user_ids.add(msg[0])
    for msg in received_messages:
        all_user_ids.add(msg[0])

    threads = []
    for other_user_id in all_user_ids:
        # Get user info
        other_user = get_user(db, other_user_id)
        if not other_user:
            continue

        # Get last message between these users
        last_message = (
            db.query(models.Message)
            .filter(
                (
                    (models.Message.sender_id == user_id)
                    & (models.Message.recipient_id == other_user_id)
                )
                | (
                    (models.Message.sender_id == other_user_id)
                    & (models.Message.recipient_id == user_id)
                )
            )
            .order_by(models.Message.created_at.desc())
            .first()
        )

        # Count unread messages from this user
        unread_count = (
            db.query(models.Message)
            .filter(
                models.Message.sender_id == other_user_id,
                models.Message.recipient_id == user_id,
                not models.Message.is_read,
            )
            .count()
        )

        # Count total messages between these users
        total_messages = (
            db.query(models.Message)
            .filter(
                (
                    (models.Message.sender_id == user_id)
                    & (models.Message.recipient_id == other_user_id)
                )
                | (
                    (models.Message.sender_id == other_user_id)
                    & (models.Message.recipient_id == user_id)
                )
            )
            .count()
        )

        threads.append(
            {
                "other_user_id": other_user_id,
                "other_user_username": other_user.username,
                "other_user_full_name": other_user.full_name,
                "last_message": last_message,
                "unread_count": unread_count,
                "total_messages": total_messages,
            }
        )

    # Sort by last message time
    threads.sort(
        key=lambda x: x["last_message"].created_at
        if x["last_message"]
        else datetime.min,
        reverse=True,
    )

    return threads[skip : skip + limit]


def get_message_history(
    db: Session, user_id: int, other_user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Message]:
    """Get message history between two users"""
    return (
        db.query(models.Message)
        .filter(
            (
                (models.Message.sender_id == user_id)
                & (models.Message.recipient_id == other_user_id)
            )
            | (
                (models.Message.sender_id == other_user_id)
                & (models.Message.recipient_id == user_id)
            )
        )
        .order_by(models.Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def mark_messages_as_read(db: Session, user_id: int, other_user_id: int) -> int:
    """Mark all messages from a specific user as read"""
    updated_count = (
        db.query(models.Message)
        .filter(
            models.Message.sender_id == other_user_id,
            models.Message.recipient_id == user_id,
            not models.Message.is_read,
        )
        .update({"is_read": True})
    )
    db.commit()
    return updated_count


def get_unread_message_count(db: Session, user_id: int) -> int:
    """Get total unread message count for a user"""
    return (
        db.query(models.Message)
        .filter(models.Message.recipient_id == user_id, not models.Message.is_read)
        .count()
    )
