"""Orders router for managing purchases with Solana escrow"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_current_active_user
from ..schemas import Order, OrderCreate
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new order with Solana escrow"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Order service not available",
        )

    try:
        # Get the listing to verify it exists and get seller info
        listing_response = (
            supabase.table("listings")
            .select("*")
            .eq("id", order.listing_id)
            .eq("is_active", True)
            .single()
            .execute()
        )

        if not listing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
            )

        listing = listing_response.data

        # Can't buy your own listing
        if listing["user_id"] == current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot purchase your own listing",
            )

        # Calculate total amount
        total_amount = listing["price"] * order.quantity

        # TODO: Call Solana smart contract initializeEscrow function
        # This would:
        # 1. Transfer SOL from buyer to escrow contract
        # 2. Create escrow account holding the funds
        # 3. Return transaction hash
        escrow_tx_hash = "placeholder_tx_hash"  # Replace with actual Solana transaction

        # Create the order
        order_data = {
            "buyer_id": current_user["id"],
            "seller_id": listing["user_id"],
            "listing_id": order.listing_id,
            "quantity": order.quantity,
            "total_amount": total_amount,
            "delivery_address": order.delivery_address,
            "notes": order.notes,
            "escrow_tx_hash": escrow_tx_hash,
            "status": "pending",
        }

        response = supabase.table("orders").insert(order_data).execute()

        if response.data:
            logger.info(f"Order created: {response.data[0]['id']}")
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create order",
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        )


@router.get("/{order_id}", response_model=Order)
async def read_order(
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Get order details"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Order service not available",
        )

    try:
        # Get the order
        order_response = (
            supabase.table("orders").select("*").eq("id", order_id).single().execute()
        )

        if not order_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        order = order_response.data

        # Only buyer or seller can view the order
        if (
            order["buyer_id"] != current_user["id"]
            and order["seller_id"] != current_user["id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order",
            )

        return order

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order: {str(e)}",
        )


@router.post("/{order_id}/confirm-delivery", response_model=Order)
async def confirm_delivery(
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Confirm delivery and release escrow funds"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Order service not available",
        )

    try:
        # Get the order
        order_response = (
            supabase.table("orders").select("*").eq("id", order_id).single().execute()
        )

        if not order_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        order = order_response.data

        # Only buyer can confirm delivery
        if order["buyer_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only buyer can confirm delivery",
            )

        # Check if order is in correct state
        if order["status"] not in ["shipped", "paid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must be shipped before confirming delivery",
            )

        # TODO: Call Solana smart contract releaseFunds function
        # This would transfer funds from escrow to seller

        # Update order status to completed
        update_response = (
            supabase.table("orders")
            .update({"status": "completed"})
            .eq("id", order_id)
            .execute()
        )

        if update_response.data:
            logger.info(f"Order {order_id} confirmed delivery")
            return update_response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update order status",
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error confirming delivery for order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm delivery: {str(e)}",
        )


@router.post("/{order_id}/dispute", response_model=Order)
async def dispute_order(
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Raise a dispute for an order"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Order service not available",
        )

    try:
        # Get the order
        order_response = (
            supabase.table("orders").select("*").eq("id", order_id).single().execute()
        )

        if not order_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        order = order_response.data

        # Only buyer can dispute
        if order["buyer_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only buyer can dispute an order",
            )

        # Check if order can be disputed
        if order["status"] in ["completed", "cancelled", "disputed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order cannot be disputed in its current state",
            )

        # Update order status to disputed
        update_response = (
            supabase.table("orders")
            .update({"status": "disputed"})
            .eq("id", order_id)
            .execute()
        )

        if update_response.data:
            logger.info(f"Order {order_id} disputed")
            # TODO: Notify admin/campus moderator about the dispute
            return update_response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update order status",
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error disputing order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispute order: {str(e)}",
        )
