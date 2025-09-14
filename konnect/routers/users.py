"""Users router"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..dependencies import get_current_active_user
from ..schemas import User, RecommendationResponse
from ..redis_client import redis_client

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.get("/me/recommendations", response_model=RecommendationResponse)
async def get_user_recommendations(current_user: User = Depends(get_current_active_user)):
    """Get cached recommendations for the current user"""
    # Try to get recommendations from Redis cache
    listing_ids = redis_client.get_user_recommendations(current_user.id)
    
    if listing_ids is None:
        # No cached recommendations found
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Please check back later as our system generates new recommendations periodically."
        )
    
    # Calculate cache expiration time (approximate)
    cached_at = datetime.utcnow() - timedelta(minutes=30)  # Estimate
    expires_at = cached_at + timedelta(hours=1)  # Assuming 1 hour cache
    
    return RecommendationResponse(
        user_id=current_user.id,
        listing_ids=listing_ids,
        cached_at=cached_at,
        expires_at=expires_at
    )
