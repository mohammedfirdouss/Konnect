"""Listings router for CRUD operations on marketplace listings"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import get_current_active_user
from ..schemas import ListingCreate, ListingUpdate
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing: ListingCreate,
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new listing (requires authentication)"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Listing service not available",
        )

    try:
        # Verify the marketplace exists
        marketplace_response = (
            supabase.table("marketplaces")
            .select("id")
            .eq("id", listing.marketplace_id)
            .single()
            .execute()
        )
        if not marketplace_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Marketplace not found"
            )

        # Create the listing
        listing_data = {
            "title": listing.title,
            "description": listing.description,
            "price": listing.price,
            "category": listing.category,
            "marketplace_id": listing.marketplace_id,
            "user_id": current_user["id"],
        }

        response = supabase.table("listings").insert(listing_data).execute()

        if response.data:
            logger.info(f"Listing created: {response.data[0]['id']}")
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create listing",
            )
    except Exception as e:
        logger.error(f"Error creating listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create listing: {str(e)}",
        )


@router.get("/")
async def read_listings(
    skip: int = Query(0, ge=0, description="Number of listings to skip"),
    limit: int = Query(
        100, ge=1, le=100, description="Maximum number of listings to return"
    ),
    marketplace_id: Optional[int] = Query(None, description="Filter by marketplace ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """Get listings with pagination and optional filtering"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Listing service not available",
        )

    try:
        query = (
            supabase.table("listings")
            .select(
                "*, profiles!listings_user_id_fkey(username), marketplaces!listings_marketplace_id_fkey(name)"
            )
            .eq("is_active", True)
        )

        if marketplace_id:
            query = query.eq("marketplace_id", marketplace_id)
        if category:
            query = query.eq("category", category)

        response = query.range(skip, skip + limit - 1).execute()

        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching listings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch listings: {str(e)}",
        )


@router.get("/{listing_id}")
async def read_listing(listing_id: int):
    """Get a single listing by ID"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Listing service not available",
        )

    try:
        response = (
            supabase.table("listings")
            .select(
                "*, profiles!listings_user_id_fkey(username, full_name), marketplaces!listings_marketplace_id_fkey(name)"
            )
            .eq("id", listing_id)
            .eq("is_active", True)
            .single()
            .execute()
        )

        if response.data:
            return response.data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
            )
    except Exception as e:
        logger.error(f"Error fetching listing {listing_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch listing: {str(e)}",
        )


@router.put("/{listing_id}")
async def update_listing(
    listing_id: int,
    listing_update: ListingUpdate,
    current_user: dict = Depends(get_current_active_user),
):
    """Update a listing (only the owner can update)"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Listing service not available",
        )

    try:
        # Update the listing (RLS will ensure only owner can update)
        update_data = listing_update.model_dump(exclude_unset=True)

        response = (
            supabase.table("listings")
            .update(update_data)
            .eq("id", listing_id)
            .eq("user_id", current_user["id"])
            .execute()
        )

        if response.data:
            logger.info(f"Listing updated: {listing_id}")
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found or not authorized",
            )
    except Exception as e:
        logger.error(f"Error updating listing {listing_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update listing: {str(e)}",
        )


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a listing (only the owner or admin can delete)"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Listing service not available",
        )

    try:
        # Soft delete the listing (set is_active to false)
        response = (
            supabase.table("listings")
            .update({"is_active": False})
            .eq("id", listing_id)
            .eq("user_id", current_user["id"])
            .execute()
        )

        if response.data:
            logger.info(f"Listing deleted: {listing_id}")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found or not authorized",
            )
    except Exception as e:
        logger.error(f"Error deleting listing {listing_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete listing: {str(e)}",
        )
