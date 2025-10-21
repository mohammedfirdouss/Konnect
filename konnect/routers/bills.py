"""Bills and subscriptions router"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import get_current_active_user
from ..schemas import (
    BillPayment,
    BillPaymentCreate,
    BillPaymentResponse,
)
from ..supabase_client import supabase
from .gamification import award_points, POINTS_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bills", tags=["bills"])


@router.post("/", response_model=BillPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_bill_payment(
    bill: BillPaymentCreate,
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new bill payment request"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bills service not available",
        )

    try:
        # Create bill payment record
        bill_data = {
            "user_id": current_user["id"],
            "bill_type": bill.bill_type,
            "amount": bill.amount,
            "description": bill.description,
            "due_date": bill.due_date.isoformat() if bill.due_date else None,
            "status": "pending",
        }

        response = supabase.table("bill_payments").insert(bill_data).execute()

        if response.data:
            bill_payment = response.data[0]
            
            # Award points for bill payment
            points_awarded = 0
            if bill.bill_type in ["tuition", "housing", "meal_plan"]:
                points_awarded = POINTS_CONFIG.get("bill_payment", 100)
                award_points(
                    current_user["id"],
                    points_awarded,
                    "bill_payment",
                    f"Bill payment created: {bill.bill_type}",
                    bill_payment["id"],
                    "bill_payment"
                )

            logger.info(f"Bill payment created: {bill_payment['id']}")
            return BillPaymentResponse(
                message="Bill payment created successfully",
                bill_payment=bill_payment,
                points_awarded=points_awarded,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create bill payment",
            )

    except Exception as e:
        logger.error(f"Error creating bill payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bill payment: {str(e)}",
        )


@router.get("/", response_model=List[BillPayment])
async def get_user_bills(
    current_user: dict = Depends(get_current_active_user),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get user's bill payments"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bills service not available",
        )

    try:
        query = (
            supabase.table("bill_payments")
            .select("*")
            .eq("user_id", current_user["id"])
            .order("created_at", desc=True)
        )

        if status_filter:
            query = query.eq("status", status_filter)

        response = query.range(skip, skip + limit - 1).execute()

        return response.data or []

    except Exception as e:
        logger.error(f"Error fetching user bills: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bills",
        )


@router.get("/{bill_id}", response_model=BillPayment)
async def get_bill_payment(
    bill_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Get specific bill payment details"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bills service not available",
        )

    try:
        response = (
            supabase.table("bill_payments")
            .select("*")
            .eq("id", bill_id)
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        if response.data:
            return response.data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill payment not found",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bill payment {bill_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bill payment",
        )


@router.post("/{bill_id}/pay", response_model=BillPaymentResponse)
async def pay_bill(
    bill_id: int,
    payment_method: str = "solana",
    current_user: dict = Depends(get_current_active_user),
):
    """Process bill payment"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bills service not available",
        )

    try:
        # Get the bill payment
        bill_response = (
            supabase.table("bill_payments")
            .select("*")
            .eq("id", bill_id)
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        if not bill_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill payment not found",
            )

        bill = bill_response.data

        if bill["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bill payment is not in pending status",
            )

        # TODO: Process actual payment with Solana
        # For now, simulate successful payment
        transaction_hash = f"simulated_tx_{bill_id}_{datetime.utcnow().timestamp()}"

        # Update bill payment status
        update_response = (
            supabase.table("bill_payments")
            .update({
                "status": "paid",
                "payment_method": payment_method,
                "transaction_hash": transaction_hash,
                "updated_at": datetime.utcnow().isoformat(),
            })
            .eq("id", bill_id)
            .execute()
        )

        if update_response.data:
            # Award points for successful payment
            points_awarded = POINTS_CONFIG.get("bill_payment_completed", 150)
            award_points(
                current_user["id"],
                points_awarded,
                "bill_payment_completed",
                f"Bill payment completed: {bill['bill_type']}",
                bill_id,
                "bill_payment"
            )

            logger.info(f"Bill payment {bill_id} completed")
            return BillPaymentResponse(
                message="Bill payment completed successfully",
                bill_payment=update_response.data[0],
                points_awarded=points_awarded,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update bill payment",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing bill payment {bill_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process bill payment: {str(e)}",
        )


@router.get("/summary/stats")
async def get_bills_summary(
    current_user: dict = Depends(get_current_active_user),
):
    """Get user's bills summary statistics"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bills service not available",
        )

    try:
        # Get all user's bills
        response = (
            supabase.table("bill_payments")
            .select("*")
            .eq("user_id", current_user["id"])
            .execute()
        )

        bills = response.data or []

        # Calculate statistics
        total_bills = len(bills)
        paid_bills = len([b for b in bills if b["status"] == "paid"])
        pending_bills = len([b for b in bills if b["status"] == "pending"])
        overdue_bills = len([b for b in bills if b["status"] == "overdue"])
        
        total_amount = sum(b["amount"] for b in bills)
        paid_amount = sum(b["amount"] for b in bills if b["status"] == "paid"])
        pending_amount = sum(b["amount"] for b in bills if b["status"] == "pending"])

        # Group by bill type
        bill_types = {}
        for bill in bills:
            bill_type = bill["bill_type"]
            if bill_type not in bill_types:
                bill_types[bill_type] = {"count": 0, "total_amount": 0}
            bill_types[bill_type]["count"] += 1
            bill_types[bill_type]["total_amount"] += bill["amount"]

        # Generate AI-powered financial insights
        ai_insights = None
        try:
            from ..routers.ai import generate_ai_response, AI_SERVICE_ENABLED
            
            if AI_SERVICE_ENABLED:
                context = f"""
                User Bill Payment Profile:
                - Total Bills: {total_bills}
                - Paid Bills: {paid_bills}
                - Pending Bills: {pending_bills}
                - Overdue Bills: {overdue_bills}
                - Total Amount: ${total_amount:.2f}
                - Paid Amount: ${paid_amount:.2f}
                - Pending Amount: ${pending_amount:.2f}
                - Payment Rate: {(paid_bills / total_bills * 100) if total_bills > 0 else 0:.1f}%
                
                Bill Types: {list(bill_types.keys())}
                
                Provide financial insights and recommendations for better bill management.
                """
                
                ai_insights = generate_ai_response(
                    "Analyze this user's bill payment patterns and provide financial advice:",
                    context
                )
        except Exception as e:
            logger.warning(f"AI bills insights failed: {e}")

        result = {
            "total_bills": total_bills,
            "paid_bills": paid_bills,
            "pending_bills": pending_bills,
            "overdue_bills": overdue_bills,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "pending_amount": pending_amount,
            "bill_types": bill_types,
            "payment_rate": (paid_bills / total_bills * 100) if total_bills > 0 else 0,
        }
        
        if ai_insights:
            result["ai_insights"] = ai_insights

        return result

    except Exception as e:
        logger.error(f"Error fetching bills summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bills summary",
        )