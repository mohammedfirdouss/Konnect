"""Users router"""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_active_user
from ..redis_client import redis_client

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.get("/me/recommendations", response_model=schemas.RecommendationResponse)
async def get_user_recommendations(
    current_user: schemas.User = Depends(get_current_active_user),
):
    """Get cached recommendations for the current user"""
    # Try to get recommendations from Redis cache
    listing_ids = redis_client.get_user_recommendations(current_user.id)

    if listing_ids is None:
        # No cached recommendations found
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Please check back later as our system generates new recommendations periodically.",
        )

    # Calculate cache expiration time (approximate)
    cached_at = datetime.utcnow() - timedelta(minutes=30)  # Estimate
    expires_at = cached_at + timedelta(hours=1)  # Assuming 1 hour cache

    return schemas.RecommendationResponse(
        user_id=current_user.id,
        listing_ids=listing_ids,
        cached_at=cached_at,
        expires_at=expires_at,
    )


# User Reviews endpoints
@router.post("/{user_id}/reviews", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
async def create_user_review(
    user_id: int,
    review: schemas.ReviewCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit a review for another user after a completed transaction"""
    # Validate that the user is reviewing someone else
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot review yourself"
        )
    
    # Validate that the reviewed user exists
    reviewed_user = crud.get_user(db, user_id)
    if not reviewed_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Set the reviewed_user_id to match the URL parameter
    review.reviewed_user_id = user_id
    
    try:
        db_review = crud.create_user_review(db, review, current_user.id)
        return db_review
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}/reviews", response_model=List[schemas.ReviewWithDetails])
async def get_user_reviews(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Retrieve all reviews for a specific user"""
    # Validate that the user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    reviews = crud.get_user_reviews(db, user_id, skip, limit)
    
    # Add reviewer details to each review
    reviews_with_details = []
    for review in reviews:
        reviewer = crud.get_user(db, review.reviewer_id)
        review_dict = review.__dict__.copy()
        review_dict['reviewer_username'] = reviewer.username if reviewer else "Unknown"
        review_dict['reviewer_full_name'] = reviewer.full_name if reviewer else None
        reviews_with_details.append(schemas.ReviewWithDetails(**review_dict))
    
    return reviews_with_details


@router.get("/{user_id}/reviews/summary", response_model=schemas.UserReviewSummary)
async def get_user_review_summary(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get review summary for a user (total reviews, average rating, distribution)"""
    # Validate that the user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    summary = crud.get_user_review_summary(db, user_id)
    return schemas.UserReviewSummary(**summary)


# User Wishlist endpoints
@router.get("/me/wishlist", response_model=schemas.WishlistResponse)
async def get_user_wishlist(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve the list of listings that the current user has saved to their wishlist"""
    wishlist_items = crud.get_wishlist_with_details(db, current_user.id, skip, limit)
    
    return schemas.WishlistResponse(
        items=wishlist_items,
        total_count=len(wishlist_items)
    )


@router.post("/me/wishlist/{listing_id}", response_model=schemas.WishlistItem, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    listing_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add a specific listing to the current user's wishlist"""
    try:
        wishlist_item = crud.add_to_wishlist(db, current_user.id, listing_id)
        return wishlist_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me/wishlist/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    listing_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove a listing from the user's wishlist"""
    success = crud.remove_from_wishlist(db, current_user.id, listing_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found in wishlist"
        )
