"""Marketplaces router for university marketplace management"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..dependencies import get_current_active_user
from ..schemas import Marketplace, MarketplaceRequest, MarketplaceRequestResponse, User

router = APIRouter(prefix="/marketplaces", tags=["marketplaces"])


@router.get("/", response_model=List[Marketplace])
async def read_marketplaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all available marketplaces"""
    marketplaces = crud.get_marketplaces(db, skip=skip, limit=limit)
    return marketplaces


@router.get("/{marketplace_id}", response_model=Marketplace)
async def read_marketplace(marketplace_id: int, db: Session = Depends(get_db)):
    """Get a specific marketplace by ID"""
    marketplace = crud.get_marketplace(db, marketplace_id)
    if not marketplace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Marketplace not found"
        )
    return marketplace


@router.get("/{marketplace_id}/products")
async def get_marketplace_products(
    marketplace_id: int,
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db),
):
    """Get all product listings for a specific marketplace"""
    # Verify marketplace exists
    marketplace = crud.get_marketplace(db, marketplace_id)
    if not marketplace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Marketplace not found"
        )

    # Get listings for this marketplace
    listings = crud.get_listings(
        db, skip=skip, limit=limit, marketplace_id=marketplace_id, category=category
    )
    return {
        "marketplace": marketplace,
        "products": listings,
        "total_count": len(listings),
    }


@router.post(
    "/request",
    response_model=MarketplaceRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_marketplace(
    request: MarketplaceRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Request creation of a new marketplace for a university"""
    # Create marketplace request
    marketplace_request = crud.create_marketplace_request(db, request, current_user.id)

    # TODO: Trigger smart contract factory call here
    # This would call a Solana smart contract to create a new marketplace instance
    # For now, we'll just store the request

    return marketplace_request
