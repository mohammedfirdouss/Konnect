"""Messages router for direct messaging"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
async def send_message(
    message: schemas.MessageCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Send a direct message to another user"""
    # Validate recipient exists
    recipient = crud.get_user(db, message.recipient_id)
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found"
        )

    # Prevent sending message to self
    if message.recipient_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send a message to yourself",
        )

    # Validate listing if provided
    if message.listing_id:
        listing = crud.get_listing(db, message.listing_id)
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
            )

    # Create message
    db_message = crud.create_message(db, message, current_user.id)
    
    # Send notification to recipient
    from .notifications import notify_new_message
    notify_new_message(current_user.id, message.recipient_id, message.listing_id)
    
    return db_message


@router.get("/threads", response_model=schemas.MessageThreadResponse)
async def get_message_threads(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve all of the current user's message threads (conversations)"""
    threads_data = crud.get_message_threads(db, current_user.id, skip, limit)

    # Convert to schema format
    threads = []
    for thread_data in threads_data:
        thread = schemas.MessageThread(
            other_user_id=thread_data["other_user_id"],
            other_user_username=thread_data["other_user_username"],
            other_user_full_name=thread_data["other_user_full_name"],
            last_message=thread_data["last_message"],
            unread_count=thread_data["unread_count"],
            total_messages=thread_data["total_messages"],
        )
        threads.append(thread)

    return schemas.MessageThreadResponse(threads=threads, total_count=len(threads))


@router.get("/threads/{user_id}", response_model=schemas.MessageHistoryResponse)
async def get_message_history(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve the full message history between the current user and another specific user"""
    # Validate other user exists
    other_user = crud.get_user(db, user_id)
    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Prevent getting history with self
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot get message history with yourself",
        )

    # Get message history
    messages = crud.get_message_history(db, current_user.id, user_id, skip, limit)

    # Add sender and recipient details to messages
    messages_with_details = []
    for message in messages:
        sender = crud.get_user(db, message.sender_id)
        recipient = crud.get_user(db, message.recipient_id)
        listing = (
            crud.get_listing(db, message.listing_id) if message.listing_id else None
        )

        message_dict = message.__dict__.copy()
        message_dict["sender_username"] = sender.username if sender else "Unknown"
        message_dict["sender_full_name"] = sender.full_name if sender else None
        message_dict["recipient_username"] = (
            recipient.username if recipient else "Unknown"
        )
        message_dict["recipient_full_name"] = recipient.full_name if recipient else None
        message_dict["listing_title"] = listing.title if listing else None

        messages_with_details.append(schemas.MessageWithDetails(**message_dict))

    # Mark messages as read
    crud.mark_messages_as_read(db, current_user.id, user_id)

    return schemas.MessageHistoryResponse(
        messages=messages_with_details,
        other_user_id=user_id,
        other_user_username=other_user.username,
        other_user_full_name=other_user.full_name,
        total_count=len(messages_with_details),
    )


@router.get("/unread-count", response_model=dict)
async def get_unread_message_count(
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get total unread message count for the current user"""
    count = crud.get_unread_message_count(db, current_user.id)
    return {"unread_count": count}


@router.patch("/{message_id}/read", status_code=status.HTTP_200_OK)
async def mark_message_as_read(
    message_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark a specific message as read"""
    message = crud.get_message(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    # Only recipient can mark as read
    if message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only mark your own received messages as read",
        )

    # Update message
    message.is_read = True
    db.commit()
    db.refresh(message)

    return {"message": "Message marked as read"}
