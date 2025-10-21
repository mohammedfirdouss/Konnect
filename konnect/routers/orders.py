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

        # Call Solana smart contract to create escrow
        from ..solana_client import create_escrow_account

        # For now, use placeholder keys - in production these would come from user profiles
        buyer_public_key = "placeholder_buyer_key"
        seller_public_key = "placeholder_seller_key"

        success, escrow_tx_hash, escrow_account = create_escrow_account(
            buyer_public_key=buyer_public_key,
            seller_public_key=seller_public_key,
            amount=total_amount,
            order_id=0,  # Will be updated after order creation
        )

        if not success:
            logger.warning("Failed to create escrow account for order")
            escrow_tx_hash = "escrow_failed"

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
            order_data = response.data[0]
            logger.info(f"Order created: {order_data['id']}")

            # Award points for creating order
            from .gamification import award_points

            award_points(
                current_user["id"],
                10,  # Points for creating order
                "order_created",
                f"Order created for listing {order.listing_id}",
                order_data["id"],
                "order",
            )

            # Send notification to seller
            from .notifications import notify_order_update

            notify_order_update(order_data["id"], "pending", listing["user_id"])

            return order_data
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

        # Call Solana smart contract to release escrow funds
        from ..solana_client import release_escrow_funds

        # Get escrow account address from order
        escrow_account = order.get("escrow_account", "placeholder_escrow")
        seller_public_key = "placeholder_seller_key"  # Would come from seller profile

        success, release_tx_hash = release_escrow_funds(
            escrow_account_address=escrow_account,
            seller_public_key=seller_public_key,
            order_id=order_id,
        )

        if success:
            logger.info(
                f"Escrow funds released for order {order_id}, tx: {release_tx_hash}"
            )
        else:
            logger.warning(f"Failed to release escrow funds for order {order_id}")

        # Update order status to completed
        update_response = (
            supabase.table("orders")
            .update({"status": "completed"})
            .eq("id", order_id)
            .execute()
        )

        if update_response.data:
            logger.info(f"Order {order_id} confirmed delivery")

            # Award points for completing order
            from .gamification import award_points

            award_points(
                current_user["id"],
                50,  # Points for completing order
                "order_completed",
                f"Order {order_id} completed",
                order_id,
                "order",
            )

            # Award points to seller
            award_points(
                order["seller_id"],
                100,  # Points for sale completed
                "sale_completed",
                f"Sale completed for order {order_id}",
                order_id,
                "order",
            )

            # Send notifications
            from .notifications import notify_order_update, notify_delivery_confirmed

            notify_order_update(order_id, "completed", order["seller_id"])
            notify_delivery_confirmed(order_id, current_user["id"])

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

            # Send notifications
            from .notifications import notify_order_update

            notify_order_update(order_id, "disputed", order["seller_id"])

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
