"""Admin router for seller verification and content moderation"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..dependencies import require_admin_role
from ..schemas import (
    AdminStats,
    PendingSeller,
    SellerVerificationRequest,
    SellerVerificationResponse,
    User,
    FraudDetectionResponse,
)
from ..agents.fraud_detection import create_fraud_detection_agent

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Get admin dashboard statistics"""
    stats = crud.get_admin_stats(db)
    return stats


@router.get("/marketplace/sellers/pending", response_model=List[PendingSeller])
async def get_pending_sellers(
    current_user: User = Depends(require_admin_role),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get list of sellers awaiting verification"""
    pending_sellers = crud.get_pending_sellers(db, skip=skip, limit=limit)
    return pending_sellers


@router.post(
    "/marketplace/sellers/{seller_id}/verify", response_model=SellerVerificationResponse
)
async def verify_seller(
    seller_id: int,
    verification_request: SellerVerificationRequest,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Verify a seller and mint verification NFT"""
    # Get the seller
    seller = crud.get_user(db, seller_id)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found"
        )

    if seller.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a seller"
        )

    if seller.is_verified_seller:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Seller is already verified"
        )

    # TODO: Mint verification NFT on Solana
    # This would call a smart contract to mint an NFT proving seller verification
    nft_mint_tx_hash = "placeholder_nft_mint_tx_hash"  # Replace with actual transaction

    # Update seller verification status
    updated_seller = crud.verify_seller(db, seller_id, nft_mint_tx_hash)

    return SellerVerificationResponse(
        seller_id=seller_id,
        verified=True,
        nft_mint_tx_hash=nft_mint_tx_hash,
        verified_at=updated_seller.verified_at,
    )


@router.delete(
    "/marketplace/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_listing(
    product_id: int,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Remove a fraudulent or inappropriate listing"""
    # Get the listing
    listing = crud.get_listing(db, product_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    # Delete the listing (admin forced removal)
    success = crud.force_delete_listing(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove listing",
        )


@router.get("/marketplace/requests", response_model=List[dict])
async def get_marketplace_requests(
    current_user: User = Depends(require_admin_role),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get pending marketplace creation requests"""
    requests = crud.get_pending_marketplace_requests(db, skip=skip, limit=limit)
    return requests


@router.post("/marketplace/requests/{request_id}/approve")
async def approve_marketplace_request(
    request_id: int,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Approve a marketplace creation request"""
    # Get the request
    request = crud.get_marketplace_request(db, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace request not found",
        )

    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request has already been processed",
        )

    # TODO: Create the marketplace via smart contract
    # This would deploy a new marketplace contract instance
    contract_tx_hash = "placeholder_contract_tx_hash"

    # Approve the request and create marketplace
    marketplace = crud.approve_marketplace_request(db, request_id, contract_tx_hash)

    return {
        "message": "Marketplace request approved",
        "marketplace": marketplace,
        "contract_tx_hash": contract_tx_hash,
    }


@router.post("/marketplace/requests/{request_id}/reject")
async def reject_marketplace_request(
    request_id: int,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """Reject a marketplace creation request"""
    # Get the request
    request = crud.get_marketplace_request(db, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace request not found",
        )

    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request has already been processed",
        )

    # Reject the request
    updated_request = crud.reject_marketplace_request(db, request_id)

    return {"message": "Marketplace request rejected", "request": updated_request}


# AI Fraud Detection Reports
@router.get("/ai/fraud-reports", response_model=FraudDetectionResponse)
async def get_fraud_reports(
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(require_admin_role),
):
    """Get AI-powered fraud detection reports for admin review"""
    try:
        # Create fraud detection agent
        agent = create_fraud_detection_agent()

        # Get fraud reports
        reports = agent.get_fraud_reports(limit=page_size)

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
        raise HTTPException(
            status_code=503,
            detail=f"AI fraud detection service temporarily unavailable: {str(e)}",
        )
