"""Listings router for CRUD operations on marketplace listings"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..dependencies import get_current_active_user
from ..schemas import Listing, ListingCreate, ListingUpdate, User

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("/", response_model=Listing, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing: ListingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new listing (requires authentication)"""
    # Verify the marketplace exists
    marketplace = crud.get_marketplace(db, listing.marketplace_id)
    if not marketplace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Marketplace not found"
        )

    # Create the listing
    db_listing = crud.create_listing(db, listing, current_user.id)
    return db_listing


@router.get("/", response_model=List[Listing])
async def read_listings(
    skip: int = Query(0, ge=0, description="Number of listings to skip"),
    limit: int = Query(
        100, ge=1, le=100, description="Maximum number of listings to return"
    ),
    marketplace_id: Optional[int] = Query(None, description="Filter by marketplace ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    """Get listings with pagination and optional filtering"""
    listings = crud.get_listings(
        db, skip=skip, limit=limit, marketplace_id=marketplace_id, category=category
    )
    return listings


@router.get("/{listing_id}", response_model=Listing)
async def read_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get a single listing by ID"""
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )
    if not listing.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )
    return listing


@router.put("/{listing_id}", response_model=Listing)
async def update_listing(
    listing_id: int,
    listing_update: ListingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a listing (only the owner can update)"""
    # Get the listing
    db_listing = crud.get_listing(db, listing_id)
    if not db_listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    # Check if the current user is the owner
    if db_listing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this listing",
        )

    # Update the listing
    updated_listing = crud.update_listing(db, listing_id, listing_update)
    return updated_listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a listing (only the owner or admin can delete)"""
    # Get the listing
    db_listing = crud.get_listing(db, listing_id)
    if not db_listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    # Check if the current user is the owner
    # Note: Admin functionality would need to be implemented separately
    # For now, only the owner can delete
    if db_listing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this listing",
        )

    # Delete the listing (soft delete)
    success = crud.delete_listing(db, listing_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete listing",
        )
