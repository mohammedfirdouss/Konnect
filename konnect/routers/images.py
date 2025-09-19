"""Images router for listing image uploads"""

import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(prefix="/listings", tags=["images"])

# Configuration for file uploads
UPLOAD_DIR = "uploads/images"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Check file extension
    if file.filename:
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
            )


def save_uploaded_file(file: UploadFile, listing_id: int) -> tuple[str, str, int]:
    """Save uploaded file and return filename, filepath, and size"""
    # Generate unique filename
    file_ext = os.path.splitext(file.filename.lower())[1]
    unique_filename = f"{listing_id}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
        file_size = len(content)

    return unique_filename, file_path, file_size


@router.post(
    "/{listing_id}/images",
    response_model=schemas.ListingImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_listing_images(
    listing_id: int,
    files: List[UploadFile] = File(...),
    is_primary: bool = False,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload one or more images for a specific listing"""
    # Verify listing exists and user owns it
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    if listing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload images to your own listings",
        )

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided"
        )

    if len(files) > 10:  # Limit number of images per listing
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images allowed per listing",
        )

    uploaded_images = []

    try:
        for i, file in enumerate(files):
            # Validate file
            validate_image_file(file)

            # Save file
            filename, file_path, file_size = save_uploaded_file(file, listing_id)

            # Set first image as primary if requested
            set_as_primary = is_primary and i == 0

            # Create database record
            db_image = crud.create_listing_image(
                db=db,
                listing_id=listing_id,
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=file.content_type or "image/jpeg",
                is_primary=set_as_primary,
            )

            uploaded_images.append(db_image)

        # Return the first uploaded image (or all if single upload)
        if uploaded_images:
            return uploaded_images[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload images",
            )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up uploaded files on error
        for image in uploaded_images:
            try:
                if os.path.exists(image.file_path):
                    os.remove(image.file_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload images: {str(e)}",
        )


@router.get("/{listing_id}/images", response_model=List[schemas.ListingImage])
async def get_listing_images(
    listing_id: int,
    db: Session = Depends(get_db),
):
    """Get all images for a specific listing"""
    # Verify listing exists
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    images = crud.get_listing_images(db, listing_id)
    return images


@router.delete(
    "/{listing_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_listing_image(
    listing_id: int,
    image_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a specific image from a listing"""
    # Verify listing exists and user owns it
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    if listing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete images from your own listings",
        )

    # Get image to delete
    image = crud.get_listing_image(db, image_id)
    if not image or image.listing_id != listing_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    # Delete file from filesystem
    try:
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
    except Exception:
        pass  # Continue even if file deletion fails

    # Delete from database
    success = crud.delete_listing_image(db, image_id, listing_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image",
        )


@router.patch("/{listing_id}/images/{image_id}/primary", status_code=status.HTTP_200_OK)
async def set_primary_image(
    listing_id: int,
    image_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Set an image as the primary image for a listing"""
    # Verify listing exists and user owns it
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    if listing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify images for your own listings",
        )

    # Set as primary
    success = crud.set_primary_image(db, image_id, listing_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    return {"message": "Primary image updated successfully"}
