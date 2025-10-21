"""Notifications router"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import get_current_active_user
from ..schemas import (
    NotificationResponse,
)
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    related_entity_id: int = None,
    related_entity_type: str = None,
) -> bool:
    """Create a notification for a user"""
    if not supabase:
        logger.error("Supabase not available for notification creation")
        return False

    try:
        notification_data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "is_read": False,
            "related_entity_id": related_entity_id,
            "related_entity_type": related_entity_type,
        }

        response = supabase.table("notifications").insert(notification_data).execute()

        if response.data:
            logger.info(f"Notification created for user {user_id}: {title}")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        return False


def notify_order_update(order_id: int, status: str, user_id: int):
    """Send notification for order status update"""
    status_messages = {
        "pending": "Your order has been placed and is pending payment",
        "paid": "Payment received! Your order is being processed",
        "shipped": "Your order has been shipped and is on its way",
        "delivered": "Your order has been delivered successfully",
        "completed": "Your order has been completed",
        "cancelled": "Your order has been cancelled",
        "disputed": "A dispute has been raised for your order",
    }

    title = f"Order #{order_id} Update"
    message = status_messages.get(
        status, f"Your order status has been updated to {status}"
    )

    create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type="order_update",
        related_entity_id=order_id,
        related_entity_type="order",
    )


def notify_payment_received(order_id: int, amount: float, seller_id: int):
    """Send notification for payment received"""
    title = "Payment Received"
    message = f"You received ${amount} for order #{order_id}"

    create_notification(
        user_id=seller_id,
        title=title,
        message=message,
        notification_type="payment",
        related_entity_id=order_id,
        related_entity_type="order",
    )


def notify_delivery_confirmed(order_id: int, buyer_id: int):
    """Send notification for delivery confirmation"""
    title = "Delivery Confirmed"
    message = f"Delivery has been confirmed for order #{order_id}. Escrow funds have been released."

    create_notification(
        user_id=buyer_id,
        title=title,
        message=message,
        notification_type="delivery",
        related_entity_id=order_id,
        related_entity_type="order",
    )


def notify_bill_due(user_id: int, bill_type: str, amount: float, due_date: datetime):
    """Send notification for bill due"""
    title = "Bill Payment Due"
    message = (
        f"Your {bill_type} bill of ${amount} is due on {due_date.strftime('%Y-%m-%d')}"
    )

    create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type="bill_reminder",
        related_entity_type="bill",
    )


def notify_new_message(sender_id: int, recipient_id: int, listing_id: int = None):
    """Send notification for new message"""
    title = "New Message"
    message = "You have received a new message"

    if listing_id:
        message += " about a listing"

    create_notification(
        user_id=recipient_id,
        title=title,
        message=message,
        notification_type="message",
        related_entity_id=listing_id,
        related_entity_type="listing",
    )


@router.get("/", response_model=NotificationResponse)
async def get_notifications(
    current_user: dict = Depends(get_current_active_user),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    notification_type: Optional[str] = Query(
        None, description="Filter by notification type"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get user's notifications"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notifications service not available",
        )

    try:
        query = (
            supabase.table("notifications")
            .select("*")
            .eq("user_id", current_user["id"])
            .order("created_at", desc=True)
        )

        if is_read is not None:
            query = query.eq("is_read", is_read)
        if notification_type:
            query = query.eq("notification_type", notification_type)

        response = query.range(skip, skip + limit - 1).execute()

        notifications = response.data or []

        # Get unread count
        unread_response = (
            supabase.table("notifications")
            .select("id")
            .eq("user_id", current_user["id"])
            .eq("is_read", False)
            .execute()
        )

        unread_count = len(unread_response.data) if unread_response.data else 0

        # Get total count
        total_response = (
            supabase.table("notifications")
            .select("id")
            .eq("user_id", current_user["id"])
            .execute()
        )

        total_count = len(total_response.data) if total_response.data else 0

        return NotificationResponse(
            notifications=notifications,
            unread_count=unread_count,
            total_count=total_count,
        )

    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications",
        )


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_active_user),
):
    """Get unread notifications count"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notifications service not available",
        )

    try:
        response = (
            supabase.table("notifications")
            .select("id")
            .eq("user_id", current_user["id"])
            .eq("is_read", False)
            .execute()
        )

        unread_count = len(response.data) if response.data else 0

        return {"unread_count": unread_count}

    except Exception as e:
        logger.error(f"Error fetching unread count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch unread count",
        )


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Mark a notification as read"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notifications service not available",
        )

    try:
        # Check if notification belongs to user
        notification_response = (
            supabase.table("notifications")
            .select("*")
            .eq("id", notification_id)
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        if not notification_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        # Mark as read
        response = (
            supabase.table("notifications")
            .update(
                {
                    "is_read": True,
                    "read_at": datetime.utcnow().isoformat(),
                }
            )
            .eq("id", notification_id)
            .execute()
        )

        if response.data:
            return {"message": "Notification marked as read"}

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read",
        )


@router.patch("/mark-all-read")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_active_user),
):
    """Mark all notifications as read"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notifications service not available",
        )

    try:
        (
            supabase.table("notifications")
            .update(
                {
                    "is_read": True,
                    "read_at": datetime.utcnow().isoformat(),
                }
            )
            .eq("user_id", current_user["id"])
            .eq("is_read", False)
            .execute()
        )

        return {"message": "All notifications marked as read"}

    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read",
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a notification"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notifications service not available",
        )

    try:
        # Check if notification belongs to user
        notification_response = (
            supabase.table("notifications")
            .select("id")
            .eq("id", notification_id)
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        if not notification_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        # Delete notification
        supabase.table("notifications").delete().eq("id", notification_id).execute()

        return {"message": "Notification deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification",
        )
