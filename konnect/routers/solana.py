"""Solana blockchain router"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_current_active_user
from ..solana_client import (
    check_solana_connection,
    validate_solana_address,
    get_solana_balance,
    estimate_transaction_fee,
    get_solana_transaction_status,
    get_escrow_account_info,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/solana", tags=["solana"])


@router.get("/health")
async def solana_health_check():
    """Check Solana blockchain connection health"""
    connection_status = check_solana_connection()

    if connection_status.get("solana_available"):
        return {
            "status": "healthy",
            "service": "solana_blockchain",
            "connection": connection_status,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Solana blockchain not available: {connection_status.get('error', 'Unknown error')}",
        )


@router.get("/balance/{public_key}")
async def get_balance(
    public_key: str,
    current_user: dict = Depends(get_current_active_user),
):
    """Get SOL balance for a public key"""
    if not validate_solana_address(public_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Solana public key address",
        )

    balance = get_solana_balance(public_key)

    return {
        "public_key": public_key,
        "balance_sol": balance,
        "balance_lamports": int(balance * 1_000_000_000),
    }


@router.get("/validate-address/{address}")
async def validate_address(
    address: str,
    current_user: dict = Depends(get_current_active_user),
):
    """Validate a Solana public key address"""
    is_valid = validate_solana_address(address)

    return {
        "address": address,
        "is_valid": is_valid,
    }


@router.get("/transaction-fee")
async def get_transaction_fee(
    current_user: dict = Depends(get_current_active_user),
):
    """Get estimated transaction fee"""
    fee = estimate_transaction_fee()

    return {
        "fee_sol": fee,
        "fee_lamports": int(fee * 1_000_000_000),
    }


@router.get("/transaction/{transaction_hash}")
async def get_transaction_status(
    transaction_hash: str,
    current_user: dict = Depends(get_current_active_user),
):
    """Get status of a Solana transaction"""
    status = get_solana_transaction_status(transaction_hash)

    if "error" in status:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=status["error"],
        )

    return status


@router.get("/escrow/{escrow_address}")
async def get_escrow_info(
    escrow_address: str,
    current_user: dict = Depends(get_current_active_user),
):
    """Get information about an escrow account"""
    info = get_escrow_account_info(escrow_address)

    if "error" in info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=info["error"],
        )

    return info


@router.post("/escrow/create")
async def create_escrow(
    buyer_public_key: str,
    seller_public_key: str,
    amount: float,
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Create escrow account for an order"""
    # Validate public keys
    if not validate_solana_address(buyer_public_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid buyer public key",
        )

    if not validate_solana_address(seller_public_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid seller public key",
        )

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive",
        )

    # Import here to avoid circular imports
    from ..solana_client import create_escrow_account

    success, transaction_hash, escrow_account = create_escrow_account(
        buyer_public_key=buyer_public_key,
        seller_public_key=seller_public_key,
        amount=amount,
        order_id=order_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create escrow account",
        )

    return {
        "success": True,
        "transaction_hash": transaction_hash,
        "escrow_account": escrow_account,
        "amount": amount,
        "order_id": order_id,
    }


@router.post("/escrow/release")
async def release_escrow(
    escrow_account: str,
    seller_public_key: str,
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Release escrow funds to seller"""
    if not validate_solana_address(seller_public_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid seller public key",
        )

    # Import here to avoid circular imports
    from ..solana_client import release_escrow_funds

    success, transaction_hash = release_escrow_funds(
        escrow_account_address=escrow_account,
        seller_public_key=seller_public_key,
        order_id=order_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to release escrow funds",
        )

    return {
        "success": True,
        "transaction_hash": transaction_hash,
        "escrow_account": escrow_account,
        "order_id": order_id,
    }


@router.post("/escrow/refund")
async def refund_escrow(
    escrow_account: str,
    buyer_public_key: str,
    order_id: int,
    reason: str = "order_cancelled",
    current_user: dict = Depends(get_current_active_user),
):
    """Refund escrow funds to buyer"""
    if not validate_solana_address(buyer_public_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid buyer public key",
        )

    # Import here to avoid circular imports
    from ..solana_client import refund_escrow_funds

    success, transaction_hash = refund_escrow_funds(
        escrow_account_address=escrow_account,
        buyer_public_key=buyer_public_key,
        order_id=order_id,
        reason=reason,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refund escrow funds",
        )

    return {
        "success": True,
        "transaction_hash": transaction_hash,
        "escrow_account": escrow_account,
        "order_id": order_id,
        "reason": reason,
    }
