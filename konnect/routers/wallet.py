"""Wallet router for transaction management"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import get_current_active_user
from ..schemas import (
    WalletTransaction,
    WalletBalance,
    WalletDepositRequest,
    WalletWithdrawalRequest,
)
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["wallet"])


def get_user_wallet_balance(user_id: int) -> float:
    """Get user's current wallet balance"""
    if not supabase:
        return 0.0

    try:
        # Get the latest transaction to determine current balance
        response = (
            supabase.table("wallet_transactions")
            .select("balance_after")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]["balance_after"]
        else:
            return 0.0

    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        return 0.0


def create_wallet_transaction(
    user_id: int,
    transaction_type: str,
    amount: float,
    description: str = None,
    transaction_hash: str = None,
) -> bool:
    """Create a wallet transaction record"""
    if not supabase:
        return False

    try:
        current_balance = get_user_wallet_balance(user_id)
        
        # Calculate new balance
        if transaction_type in ["deposit", "refund"]:
            new_balance = current_balance + amount
        elif transaction_type in ["withdrawal", "payment"]:
            new_balance = current_balance - amount
        else:
            new_balance = current_balance

        # Create transaction record
        transaction_data = {
            "user_id": user_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "balance_before": current_balance,
            "balance_after": new_balance,
            "description": description,
            "transaction_hash": transaction_hash,
            "status": "completed",
        }

        response = supabase.table("wallet_transactions").insert(transaction_data).execute()

        if response.data:
            logger.info(f"Wallet transaction created: {response.data[0]['id']}")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Error creating wallet transaction: {e}")
        return False


@router.get("/balance", response_model=WalletBalance)
async def get_wallet_balance(
    current_user: dict = Depends(get_current_active_user),
):
    """Get current user's wallet balance and statistics"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Wallet service not available",
        )

    try:
        user_id = current_user["id"]
        current_balance = get_user_wallet_balance(user_id)

        # Get transaction statistics
        response = (
            supabase.table("wallet_transactions")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .execute()
        )

        transactions = response.data or []

        # Calculate totals
        total_deposited = sum(
            t["amount"] for t in transactions 
            if t["transaction_type"] in ["deposit", "refund"]
        )
        total_withdrawn = sum(
            t["amount"] for t in transactions 
            if t["transaction_type"] in ["withdrawal", "payment"]
        )
        total_spent = sum(
            t["amount"] for t in transactions 
            if t["transaction_type"] == "payment"
        )

        # Get last transaction date
        last_transaction_at = None
        if transactions:
            last_transaction = max(transactions, key=lambda x: x["created_at"])
            last_transaction_at = datetime.fromisoformat(last_transaction["created_at"])

        return WalletBalance(
            user_id=user_id,
            current_balance=current_balance,
            total_deposited=total_deposited,
            total_withdrawn=total_withdrawn,
            total_spent=total_spent,
            last_transaction_at=last_transaction_at,
        )

    except Exception as e:
        logger.error(f"Error fetching wallet balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wallet balance",
        )


@router.get("/transactions", response_model=List[WalletTransaction])
async def get_wallet_transactions(
    current_user: dict = Depends(get_current_active_user),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get user's wallet transaction history"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Wallet service not available",
        )

    try:
        query = (
            supabase.table("wallet_transactions")
            .select("*")
            .eq("user_id", current_user["id"])
            .order("created_at", desc=True)
        )

        if transaction_type:
            query = query.eq("transaction_type", transaction_type)

        response = query.range(skip, skip + limit - 1).execute()

        return response.data or []

    except Exception as e:
        logger.error(f"Error fetching wallet transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wallet transactions",
        )


@router.post("/deposit")
async def deposit_to_wallet(
    deposit_request: WalletDepositRequest,
    current_user: dict = Depends(get_current_active_user),
):
    """Deposit funds to wallet"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Wallet service not available",
        )

    if deposit_request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit amount must be positive",
        )

    try:
        # TODO: Process actual Solana deposit
        # For now, simulate successful deposit
        transaction_hash = f"deposit_{current_user['id']}_{datetime.utcnow().timestamp()}"

        success = create_wallet_transaction(
            user_id=current_user["id"],
            transaction_type="deposit",
            amount=deposit_request.amount,
            description=deposit_request.description or "Wallet deposit",
            transaction_hash=transaction_hash,
        )

        if success:
            return {
                "message": f"Successfully deposited ${deposit_request.amount} to wallet",
                "transaction_hash": transaction_hash,
                "new_balance": get_user_wallet_balance(current_user["id"]),
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process deposit",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing deposit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process deposit: {str(e)}",
        )


@router.post("/withdraw")
async def withdraw_from_wallet(
    withdrawal_request: WalletWithdrawalRequest,
    current_user: dict = Depends(get_current_active_user),
):
    """Withdraw funds from wallet"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Wallet service not available",
        )

    if withdrawal_request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Withdrawal amount must be positive",
        )

    try:
        current_balance = get_user_wallet_balance(current_user["id"])

        if current_balance < withdrawal_request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance",
            )

        # TODO: Process actual Solana withdrawal
        # For now, simulate successful withdrawal
        transaction_hash = f"withdrawal_{current_user['id']}_{datetime.utcnow().timestamp()}"

        success = create_wallet_transaction(
            user_id=current_user["id"],
            transaction_type="withdrawal",
            amount=withdrawal_request.amount,
            description=withdrawal_request.description or "Wallet withdrawal",
            transaction_hash=transaction_hash,
        )

        if success:
            return {
                "message": f"Successfully withdrew ${withdrawal_request.amount} from wallet",
                "transaction_hash": transaction_hash,
                "new_balance": get_user_wallet_balance(current_user["id"]),
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process withdrawal",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing withdrawal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process withdrawal: {str(e)}",
        )


@router.post("/pay/{order_id}")
async def pay_with_wallet(
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Pay for an order using wallet balance"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Wallet service not available",
        )

    try:
        # Get the order
        order_response = (
            supabase.table("orders")
            .select("*")
            .eq("id", order_id)
            .eq("buyer_id", current_user["id"])
            .single()
            .execute()
        )

        if not order_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        order = order_response.data

        if order["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not in pending status",
            )

        # Check wallet balance
        current_balance = get_user_wallet_balance(current_user["id"])
        if current_balance < order["total_amount"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance",
            )

        # Process payment
        transaction_hash = f"payment_{order_id}_{datetime.utcnow().timestamp()}"

        success = create_wallet_transaction(
            user_id=current_user["id"],
            transaction_type="payment",
            amount=order["total_amount"],
            description=f"Payment for order #{order_id}",
            transaction_hash=transaction_hash,
        )

        if success:
            # Update order status
            update_response = (
                supabase.table("orders")
                .update({
                    "status": "paid",
                    "updated_at": datetime.utcnow().isoformat(),
                })
                .eq("id", order_id)
                .execute()
            )

            if update_response.data:
                return {
                    "message": f"Successfully paid ${order['total_amount']} for order #{order_id}",
                    "transaction_hash": transaction_hash,
                    "new_balance": get_user_wallet_balance(current_user["id"]),
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update order status",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process payment",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing wallet payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payment: {str(e)}",
        )