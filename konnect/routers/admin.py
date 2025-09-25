"""Admin router for seller verification and content moderation"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import require_admin_role
from ..schemas import (
    AdminStats,
    PendingSeller,
    SellerVerificationRequest,
    SellerVerificationResponse,
    FraudDetectionResponse,
)
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: dict = Depends(require_admin_role),
):
    """Get admin dashboard statistics"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service not available",
        )

    try:
        # Get total users
        users_response = supabase.table("profiles").select("id", count="exact").execute()
        total_users = users_response.count if users_response.count else 0

        # Get total listings
        listings_response = supabase.table("listings").select("id", count="exact").execute()
        total_listings = listings_response.count if listings_response.count else 0

        # Get active listings
        active_listings_response = (
            supabase.table("listings")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        active_listings = active_listings_response.count if active_listings_response.count else 0

        # Get total orders
        orders_response = supabase.table("orders").select("id", count="exact").execute()
        total_orders = orders_response.count if orders_response.count else 0

        # Get pending marketplace requests
        marketplace_requests_response = (
            supabase.table("marketplace_requests")
            .select("id", count="exact")
            .eq("status", "pending")
            .execute()
        )
        pending_marketplace_requests = (
            marketplace_requests_response.count if marketplace_requests_response.count else 0
        )

        # Get verified sellers
        verified_sellers_response = (
            supabase.table("profiles")
            .select("id", count="exact")
            .eq("is_verified_seller", True)
            .execute()
        )
        verified_sellers = verified_sellers_response.count if verified_sellers_response.count else 0

        stats = AdminStats(
            total_users=total_users,
            total_listings=total_listings,
            active_listings=active_listings,
            total_orders=total_orders,
            pending_marketplace_requests=pending_marketplace_requests,
            verified_sellers=verified_sellers,
            total_revenue=0.0,  # Would be calculated from orders
            fraud_alerts=0,  # Would be calculated from fraud detection
        )

        return stats

    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch admin stats: {str(e)}",
        )


@router.get("/marketplace/sellers/pending", response_model=List[PendingSeller])
async def get_pending_sellers(
    current_user: dict = Depends(require_admin_role),
    skip: int = 0,
    limit: int = 100,
):
    """Get list of sellers awaiting verification"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service not available",
        )

    try:
        # Get profiles that are not verified sellers
        response = (
            supabase.table("profiles")
            .select("*")
            .eq("is_verified_seller", False)
            .range(skip, skip + limit - 1)
            .execute()
        )

        pending_sellers = []
        for profile in response.data or []:
            seller = PendingSeller(
                seller_id=profile["id"],
                username=profile["username"],
                full_name=profile["full_name"],
                email="",  # Would need to join with auth.users
                verification_status="pending",
                request_date=profile["created_at"],
                documents_submitted=[],  # Would be in separate table
            )
            pending_sellers.append(seller)

        return pending_sellers

    except Exception as e:
        logger.error(f"Error fetching pending sellers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending sellers: {str(e)}",
        )


@router.post(
    "/marketplace/sellers/{seller_id}/verify", response_model=SellerVerificationResponse
)
async def verify_seller(
    seller_id: str,  # Changed to string for UUID
    verification_request: SellerVerificationRequest,
    current_user: dict = Depends(require_admin_role),
):
    """Verify a seller and mint verification NFT"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service not available",
        )

    try:
        # Get the seller profile
        seller_response = (
            supabase.table("profiles")
            .select("*")
            .eq("id", seller_id)
            .single()
            .execute()
        )

        if not seller_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found"
            )

        seller = seller_response.data

        if seller["is_verified_seller"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Seller is already verified"
            )

        # TODO: Mint verification NFT on Solana
        # This would call a smart contract to mint an NFT proving seller verification
        nft_mint_tx_hash = "placeholder_nft_mint_tx_hash"  # Replace with actual transaction

        # Update seller verification status
        update_response = (
            supabase.table("profiles")
            .update({
                "is_verified_seller": True,
                "verification_nft_mint": nft_mint_tx_hash,
                "updated_at": "now()"
            })
            .eq("id", seller_id)
            .execute()
        )

        return SellerVerificationResponse(
            seller_id=seller_id,
            verified=True,
            nft_mint_tx_hash=nft_mint_tx_hash,
            verified_at=update_response.data[0]["updated_at"],
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error verifying seller {seller_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify seller: {str(e)}",
        )


@router.delete(
    "/marketplace/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_listing(
    product_id: int,
    current_user: dict = Depends(require_admin_role),
):
    """Remove a fraudulent or inappropriate listing"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service not available",
        )

    try:
        # Check if listing exists
        listing_response = (
            supabase.table("listings")
            .select("*")
            .eq("id", product_id)
            .single()
            .execute()
        )

        if not listing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
            )

        # Delete the listing (admin forced removal)
        delete_response = (
            supabase.table("listings")
            .delete()
            .eq("id", product_id)
            .execute()
        )

        return {"message": "Listing removed successfully"}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error removing listing {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove listing: {str(e)}",
        )


@router.get("/marketplace/requests", response_model=List[dict])
async def get_marketplace_requests(
    current_user: dict = Depends(require_admin_role),
    skip: int = 0,
    limit: int = 100,
):
    """Get pending marketplace creation requests"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service not available",
        )

    try:
        response = (
            supabase.table("marketplace_requests")
            .select("*")
            .range(skip, skip + limit - 1)
            .execute()
        )

        return response.data or []

    except Exception as e:
        logger.error(f"Error fetching marketplace requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch marketplace requests: {str(e)}",
        )


@router.post("/marketplace/requests/{request_id}/approve")
async def approve_marketplace_request(
    request_id: int,
    current_user: dict = Depends(require_admin_role),
):
    """Approve a marketplace creation request"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service not available",
        )

    try:
        # Get the request
        request_response = (
            supabase.table("marketplace_requests")
            .select("*")
            .eq("id", request_id)
            .single()
            .execute()
        )

        if not request_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marketplace request not found",
            )

        request = request_response.data

        if request["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request has already been processed",
            )

        # TODO: Create the marketplace via smart contract
        # This would deploy a new marketplace contract instance
        contract_tx_hash = "placeholder_contract_tx_hash"

        # Create the marketplace
        marketplace_data = {
            "name": request["university_name"],
            "description": request["description"],
            "created_by": request["requested_by"],
            "is_active": True,
            "smart_contract_address": contract_tx_hash,
        }

        marketplace_response = supabase.table("marketplaces").insert(marketplace_data).execute()

        if not marketplace_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create marketplace",
            )

        marketplace = marketplace_response.data[0]

        # Update request status
        update_response = (
            supabase.table("marketplace_requests")
            .update({
                "status": "approved",
                "smart_contract_tx_hash": contract_tx_hash,
                "updated_at": "now()"
            })
            .eq("id", request_id)
            .execute()
        )

        return {
            "message": "Marketplace request approved",
            "marketplace": marketplace,
            "contract_tx_hash": contract_tx_hash,
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error approving marketplace request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve marketplace request: {str(e)}",
        )


@router.post("/marketplace/requests/{request_id}/reject")
async def reject_marketplace_request(
    request_id: int,
    current_user: dict = Depends(require_admin_role),
):
    """Reject a marketplace creation request"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service not available",
        )

    try:
        # Get the request
        request_response = (
            supabase.table("marketplace_requests")
            .select("*")
            .eq("id", request_id)
            .single()
            .execute()
        )

        if not request_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marketplace request not found",
            )

        request = request_response.data

        if request["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request has already been processed",
            )

        # Reject the request
        update_response = (
            supabase.table("marketplace_requests")
            .update({
                "status": "rejected",
                "updated_at": "now()"
            })
            .eq("id", request_id)
            .execute()
        )

        return {"message": "Marketplace request rejected", "request": update_response.data[0]}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error rejecting marketplace request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject marketplace request: {str(e)}",
        )


# AI Fraud Detection Reports
@router.get("/ai/fraud-reports", response_model=FraudDetectionResponse)
async def get_fraud_reports(
    page: int = 1,
    page_size: int = 50,
    current_user: dict = Depends(require_admin_role),
):
    """Get AI-powered fraud detection reports for admin review"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fraud detection service not available",
        )

    try:
        # Mock fraud reports for now
        # In a real implementation, this would use AI to analyze patterns
        reports = [
            {
                "id": 1,
                "type": "suspicious_pricing",
                "risk_level": "medium",
                "description": "Listing with unusually low price",
                "target_id": 1,
                "target_type": "listing",
                "confidence": 0.7,
                "status": "pending",
                "entity_type": "listing",
            },
            {
                "id": 2,
                "type": "duplicate_listing",
                "risk_level": "low",
                "description": "Potential duplicate listing",
                "target_id": 2,
                "target_type": "listing",
                "confidence": 0.5,
                "status": "pending",
                "entity_type": "listing",
            },
        ]

        # Calculate summary statistics
        total_reports = len(reports)
        high_risk_reports = len([r for r in reports if r.get("risk_level") == "high"])
        medium_risk_reports = len(
            [r for r in reports if r.get("risk_level") == "medium"]
        )
        pending_investigation = len(
            [r for r in reports if r.get("status") == "pending"]
        )

        # Create summary
        summary = {
            "total_reports": total_reports,
            "high_risk_reports": high_risk_reports,
            "medium_risk_reports": medium_risk_reports,
            "pending_investigation": pending_investigation,
            "recent_activity": reports[:5],  # Top 5 recent reports
            "risk_trends": {
                "user_fraud": len(
                    [r for r in reports if r.get("entity_type") == "user"]
                ),
                "listing_fraud": len(
                    [r for r in reports if r.get("entity_type") == "listing"]
                ),
                "payment_fraud": 0,  # Would be calculated from payment-related reports
            },
        }

        return FraudDetectionResponse(
            reports=reports,
            summary=summary,
            total_count=total_reports,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error(f"Error fetching fraud reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI fraud detection service temporarily unavailable: {str(e)}",
        )
