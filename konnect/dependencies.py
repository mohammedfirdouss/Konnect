"""FastAPI dependencies for authentication using Supabase"""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from .supabase_client import supabase

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get the current authenticated user from Supabase token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not supabase:
        logger.error("Supabase client not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )

    try:
        response = supabase.auth.get_user(token)
        if not response.user:
            logger.warning("Invalid token provided")
            raise credentials_exception

        # Get user profile from Supabase
        profile_response = supabase.table('profiles').select('*').eq('id', response.user.id).execute()
        
        if not profile_response.data:
            logger.warning(f"Profile not found for user {response.user.id}, creating one...")
            # Create profile if it doesn't exist
            try:
                profile_data = {
                    'id': response.user.id,
                    'username': response.user.user_metadata.get('username', response.user.email.split('@')[0]),
                    'full_name': response.user.user_metadata.get('full_name', ''),
                    'role': 'buyer'
                }
                create_response = supabase.table('profiles').insert(profile_data).execute()
                if create_response.data:
                    profile = create_response.data[0]
                    logger.info(f"Created profile for user {response.user.id}")
                else:
                    logger.error(f"Failed to create profile for user {response.user.id}")
                    raise credentials_exception
            except Exception as e:
                logger.error(f"Error creating profile for user {response.user.id}: {e}")
                raise credentials_exception
        else:
            profile = profile_response.data[0]
        return {
            "id": profile["id"],
            "username": profile["username"],
            "email": response.user.email,
            "full_name": profile["full_name"],
            "role": profile["role"],
            "is_verified_seller": profile["is_verified_seller"],
            "created_at": profile["created_at"],
        }

    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get the current active user"""
    return current_user


async def require_admin_role(current_user: dict = Depends(get_current_active_user)) -> dict:
    """Require admin role for the current user"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def require_seller_role(current_user: dict = Depends(get_current_active_user)) -> dict:
    """Require seller role for the current user"""
    if current_user.get("role") not in ["seller", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Seller access required"
        )
    return current_user
