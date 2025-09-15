"""Orders router for managing purchases with Solana escrow"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..dependencies import get_current_active_user
from ..schemas import Order, OrderCreate, User

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new order with Solana escrow"""
    # Get the listing to verify it exists and get seller info
    listing = crud.get_listing(db, order.listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    if not listing.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Listing is not available"
        )

    # Can't buy your own listing
    if listing.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot purchase your own listing",
        )

    # Calculate total amount
    total_amount = listing.price * order.quantity

    # TODO: Call Solana smart contract initializeEscrow function
    # This would:
    # 1. Transfer SOL from buyer to escrow contract
    # 2. Create escrow account holding the funds
    # 3. Return transaction hash
    escrow_tx_hash = "placeholder_tx_hash"  # Replace with actual Solana transaction

    # Create the order
    db_order = crud.create_order(
        db,
        order,
        buyer_id=current_user.id,
        seller_id=listing.user_id,
        total_amount=total_amount,
        escrow_tx_hash=escrow_tx_hash,
    )

    return db_order


@router.get("/{order_id}", response_model=Order)
async def read_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get order details"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Only buyer or seller can view the order
    if order.buyer_id != current_user.id and order.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order",
        )

    return order


@router.post("/{order_id}/confirm-delivery", response_model=Order)
async def confirm_delivery(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Confirm delivery and release escrow funds"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Only buyer can confirm delivery
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyer can confirm delivery",
        )

    # Check if order is in correct state
    if order.status not in ["shipped", "paid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be shipped before confirming delivery",
        )

    # TODO: Call Solana smart contract releaseFunds function
    # This would transfer funds from escrow to seller

    # Update order status to completed
    updated_order = crud.update_order_status(db, order_id, "completed")

    return updated_order


@router.post("/{order_id}/dispute", response_model=Order)
async def dispute_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Raise a dispute for an order"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Only buyer can dispute
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyer can dispute an order",
        )

    # Check if order can be disputed
    if order.status in ["completed", "cancelled", "disputed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be disputed in its current state",
        )

    # Update order status to disputed
    updated_order = crud.update_order_status(db, order_id, "disputed")

    # TODO: Notify admin/campus moderator about the dispute

    return updated_order
