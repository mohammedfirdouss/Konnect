"""Delivery confirmation router"""

import logging
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_current_active_user
from ..schemas import (
    DeliveryConfirmationRequest,
    DeliveryConfirmationResponse,
)
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/delivery", tags=["delivery"])


def generate_delivery_code() -> str:
    """Generate a 6-digit delivery code"""
    return f"{secrets.randbelow(900000) + 100000:06d}"


def create_delivery_code(order_id: int) -> str:
    """Create a delivery code for an order"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Delivery service not available",
        )

    try:
        # Generate unique delivery code
        code = generate_delivery_code()

        # Ensure code is unique
        while True:
            existing = (
                supabase.table("delivery_codes")
                .select("id")
                .eq("code", code)
                .eq("is_used", False)
                .execute()
            )
            if not existing.data:
                break
            code = generate_delivery_code()

        # Create delivery code record
        delivery_data = {
            "order_id": order_id,
            "code": code,
            "expires_at": (
                datetime.utcnow() + timedelta(hours=24)
            ).isoformat(),  # 24 hour expiry
            "is_used": False,
        }

        response = supabase.table("delivery_codes").insert(delivery_data).execute()

        if response.data:
            logger.info(f"Delivery code created for order {order_id}: {code}")
            return code
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create delivery code",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating delivery code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create delivery code: {str(e)}",
        )


@router.post("/{order_id}/generate-code")
async def generate_delivery_code_for_order(
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Generate delivery code for an order (seller only)"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Delivery service not available",
        )

    try:
        # Get the order
        order_response = (
            supabase.table("orders").select("*").eq("id", order_id).single().execute()
        )

        if not order_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        order = order_response.data

        # Check if user is the seller
        if order["seller_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the seller can generate delivery codes",
            )

        # Check if order is in correct state
        if order["status"] not in ["paid", "shipped"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must be paid or shipped before generating delivery code",
            )

        # Check if delivery code already exists
        existing_code = (
            supabase.table("delivery_codes")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_used", False)
            .execute()
        )

        if existing_code.data:
            code_data = existing_code.data[0]
            return {
                "message": "Delivery code already exists for this order",
                "code": code_data["code"],
                "expires_at": code_data["expires_at"],
            }

        # Create new delivery code
        code = create_delivery_code(order_id)

        return {
            "message": "Delivery code generated successfully",
            "code": code,
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating delivery code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate delivery code: {str(e)}",
        )


@router.post("/confirm", response_model=DeliveryConfirmationResponse)
async def confirm_delivery(
    confirmation: DeliveryConfirmationRequest,
    current_user: dict = Depends(get_current_active_user),
):
    """Confirm delivery using delivery code"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Delivery service not available",
        )

    try:
        # Find the delivery code
        code_response = (
            supabase.table("delivery_codes")
            .select("*, orders!delivery_codes_order_id_fkey(*)")
            .eq("code", confirmation.delivery_code)
            .eq("is_used", False)
            .single()
            .execute()
        )

        if not code_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired delivery code",
            )

        code_data = code_response.data
        order = code_data["orders"]

        # Check if code is expired
        expires_at = datetime.fromisoformat(code_data["expires_at"])
        if datetime.utcnow() > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery code has expired",
            )

        # Check if user is the buyer
        if order["buyer_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the buyer can confirm delivery",
            )

        # Check if order is in correct state
        if order["status"] not in ["paid", "shipped"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not in a state that can be confirmed",
            )

        # Mark delivery code as used
        update_code_response = (
            supabase.table("delivery_codes")
            .update(
                {
                    "is_used": True,
                    "used_at": datetime.utcnow().isoformat(),
                }
            )
            .eq("id", code_data["id"])
            .execute()
        )

        if not update_code_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update delivery code",
            )

        # Update order status to completed
        update_order_response = (
            supabase.table("orders")
            .update(
                {
                    "status": "completed",
                    "updated_at": datetime.utcnow().isoformat(),
                }
            )
            .eq("id", order["id"])
            .execute()
        )

        if not update_order_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update order status",
            )

        # Call Solana smart contract to release escrow funds
        from ..solana_client import release_escrow_funds

        # Get escrow account address from order
        escrow_account = order.get("escrow_account", "placeholder_escrow")
        seller_public_key = "placeholder_seller_key"  # Would come from seller profile

        success, transaction_hash = release_escrow_funds(
            escrow_account_address=escrow_account,
            seller_public_key=seller_public_key,
            order_id=order["id"],
        )

        escrow_released = success
        if not success:
            transaction_hash = None
            logger.warning(f"Failed to release escrow funds for order {order['id']}")

        logger.info(
            f"Delivery confirmed for order {order['id']} with code {confirmation.delivery_code}"
        )

        return DeliveryConfirmationResponse(
            success=True,
            message="Delivery confirmed successfully. Escrow funds have been released.",
            order_id=order["id"],
            escrow_released=escrow_released,
            transaction_hash=transaction_hash,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming delivery: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm delivery: {str(e)}",
        )


@router.get("/{order_id}/code")
async def get_delivery_code(
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Get delivery code for an order (seller only)"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Delivery service not available",
        )

    try:
        # Get the order
        order_response = (
            supabase.table("orders").select("*").eq("id", order_id).single().execute()
        )

        if not order_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        order = order_response.data

        # Check if user is the seller
        if order["seller_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the seller can view delivery codes",
            )

        # Get delivery code
        code_response = (
            supabase.table("delivery_codes")
            .select("*")
            .eq("order_id", order_id)
            .eq("is_used", False)
            .single()
            .execute()
        )

        if not code_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active delivery code found for this order",
            )

        code_data = code_response.data

        # Check if code is expired
        expires_at = datetime.fromisoformat(code_data["expires_at"])
        if datetime.utcnow() > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery code has expired",
            )

        return {
            "code": code_data["code"],
            "expires_at": code_data["expires_at"],
            "created_at": code_data["created_at"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching delivery code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch delivery code: {str(e)}",
        )
