"""Marketplaces router for university marketplace management"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_current_active_user
from ..schemas import MarketplaceRequest
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketplaces", tags=["marketplaces"])


@router.get("/")
async def read_marketplaces(
    skip: int = 0,
    limit: int = 100,
):
    """Get all available marketplaces"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Marketplace service not available"
        )

    try:
        response = supabase.table('marketplaces').select('*, profiles!marketplaces_created_by_fkey(username)').eq('is_active', True).range(skip, skip + limit - 1).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching marketplaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch marketplaces: {str(e)}"
        )


@router.get("/{marketplace_id}")
async def read_marketplace(marketplace_id: int):
    """Get a specific marketplace by ID"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Marketplace service not available"
        )

    try:
        response = supabase.table('marketplaces').select('*, profiles!marketplaces_created_by_fkey(username)').eq('id', marketplace_id).eq('is_active', True).single().execute()
        
        if response.data:
            return response.data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Marketplace not found"
            )
    except Exception as e:
        logger.error(f"Error fetching marketplace {marketplace_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch marketplace: {str(e)}"
        )


@router.get("/{marketplace_id}/products")
async def get_marketplace_products(
    marketplace_id: int,
    skip: int = 0,
    limit: int = 100,
    category: str = None,
):
    """Get all product listings for a specific marketplace"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Marketplace service not available"
        )

    try:
        # Verify marketplace exists
        marketplace_response = supabase.table('marketplaces').select('*').eq('id', marketplace_id).eq('is_active', True).single().execute()
        if not marketplace_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Marketplace not found"
            )

        # Get listings for this marketplace
        query = supabase.table('listings').select('*, profiles!listings_user_id_fkey(username)').eq('marketplace_id', marketplace_id).eq('is_active', True)
        
        if category:
            query = query.eq('category', category)
            
        response = query.range(skip, skip + limit - 1).execute()
        
        return {
            "marketplace": marketplace_response.data,
            "products": response.data or [],
            "total_count": len(response.data) if response.data else 0,
        }
    except Exception as e:
        logger.error(f"Error fetching marketplace products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch marketplace products: {str(e)}"
        )


@router.post("/request", status_code=status.HTTP_201_CREATED)
async def request_marketplace(
    request: MarketplaceRequest,
    current_user: dict = Depends(get_current_active_user),
):
    """Request creation of a new marketplace for a university"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Marketplace service not available"
        )

    try:
        # Create marketplace request
        request_data = {
            "university_name": request.university_name,
            "university_domain": request.university_domain,
            "contact_email": request.contact_email,
            "description": request.description,
            "requested_by": current_user["id"],
        }
        
        response = supabase.table('marketplace_requests').insert(request_data).execute()
        
        if response.data:
            logger.info(f"Marketplace request created: {response.data[0]['id']}")
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create marketplace request"
            )
    except Exception as e:
        logger.error(f"Error creating marketplace request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create marketplace request: {str(e)}"
        )


@router.get("/requests/my")
async def get_my_marketplace_requests(
    current_user: dict = Depends(get_current_active_user),
):
    """Get current user's marketplace requests"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Marketplace service not available"
        )

    try:
        response = supabase.table('marketplace_requests').select('*').eq('requested_by', current_user["id"]).order('created_at', desc=True).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching user marketplace requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch marketplace requests: {str(e)}"
        )
