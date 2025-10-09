"""Images router for listing image uploads using Supabase Storage"""

import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_active_user
from ..supabase_client import supabase

router = APIRouter(prefix="/listings", tags=["images"])

# Configuration for file uploads
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
STORAGE_BUCKET_NAME = "listing_images"


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    if file.filename:
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
            )


async def upload_file_to_supabase(
    file: UploadFile, listing_id: int
) -> tuple[str, str, int]:
    """Upload file to Supabase Storage and return filename, filepath, and size"""
    file_ext = os.path.splitext(file.filename.lower())[1]
    unique_filename = f"{listing_id}_{uuid.uuid4()}{file_ext}"
    file_path = f"{listing_id}/{unique_filename}"

    content = await file.read()
    file_size = len(content)

    try:
        supabase.storage.from_(STORAGE_BUCKET_NAME).upload(file=content, path=file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload to Supabase Storage: {str(e)}",
        )

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
    """Upload one or more images for a specific listing to Supabase Storage"""
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

    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images allowed per listing",
        )

    uploaded_images = []

    for i, file in enumerate(files):
        validate_image_file(file)
        filename, file_path, file_size = await upload_file_to_supabase(file, listing_id)
        set_as_primary = is_primary and i == 0

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

    if uploaded_images:
        return uploaded_images[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload images",
        )


@router.get("/{listing_id}/images", response_model=List[schemas.ListingImage])
async def get_listing_images(
    listing_id: int,
    db: Session = Depends(get_db),
    width: Optional[int] = None,
    height: Optional[int] = None,
    resize: Optional[str] = None,  # "cover", "contain", "fill"
):
    """Get all images for a specific listing, with optional transformations."""
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    images = crud.get_listing_images(db, listing_id)

    transform_options = {}
    if width:
        transform_options["width"] = width
    if height:
        transform_options["height"] = height
    if resize:
        transform_options["resize"] = resize

    # Construct public URLs for the images
    for image in images:
        if transform_options:
            image.file_path = supabase.storage.from_(
                STORAGE_BUCKET_NAME
            ).get_public_url(image.file_path, options={"transform": transform_options})
        else:
            image.file_path = supabase.storage.from_(
                STORAGE_BUCKET_NAME
            ).get_public_url(image.file_path)

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
    """Delete a specific image from a listing and Supabase Storage"""
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

    image = crud.get_listing_image(db, image_id)
    if not image or image.listing_id != listing_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    try:
        supabase.storage.from_(STORAGE_BUCKET_NAME).remove([image.file_path])
    except Exception as e:
        # Log the error but proceed with deleting the database record
        print(f"Error deleting file from Supabase Storage: {e}")

    crud.delete_listing_image(db, image_id, listing_id)


@router.patch("/{listing_id}/images/{image_id}/primary", status_code=status.HTTP_200_OK)
async def set_primary_image(
    listing_id: int,
    image_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Set an image as the primary image for a listing"""
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

    success = crud.set_primary_image(db, image_id, listing_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    return {"message": "Primary image updated successfully"}
