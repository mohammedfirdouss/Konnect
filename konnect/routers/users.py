"""Users router"""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from .. import schemas
from ..dependencies import get_current_active_user
from ..redis_client import redis_client
from ..supabase_client import supabase

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.get("/me/recommendations", response_model=schemas.RecommendationResponse)
async def get_user_recommendations(
    current_user: dict = Depends(get_current_active_user),
):
    """Get cached recommendations for the current user"""
    # Try to get recommendations from Redis cache
    user_id = current_user["id"]
    listing_ids = redis_client.get_user_recommendations(user_id)

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
        user_id=user_id,
        listing_ids=listing_ids,
        cached_at=cached_at,
        expires_at=expires_at,
    )


@router.get("/me/profile")
async def get_user_profile(current_user: dict = Depends(get_current_active_user)):
    """Get detailed user profile information"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile service not available"
        )
    
    try:
        # Get additional profile data from Supabase
        response = supabase.table('profiles').select('*').eq('id', current_user["id"]).single().execute()
        
        if response.data:
            return response.data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )


@router.put("/me/profile")
async def update_user_profile(
    profile_update: dict,
    current_user: dict = Depends(get_current_active_user)
):
    """Update user profile information"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile service not available"
        )
    
    try:
        # Update profile in Supabase
        response = supabase.table('profiles').update(profile_update).eq('id', current_user["id"]).execute()
        
        if response.data:
            return {"message": "Profile updated successfully", "profile": response.data[0]}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
