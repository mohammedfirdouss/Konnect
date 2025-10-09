"""FastAPI dependencies for authentication using Supabase"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import AuthApiError

from .supabase_client import supabase

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get the current authenticated user from Supabase token with comprehensive error handling"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not supabase:
        logger.error("Supabase client not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured",
        )

    if not token or token.strip() == "":
        logger.warning("Empty token provided")
        raise credentials_exception

    try:
        # Validate token with Supabase
        response = supabase.auth.get_user(token)

        if not response.user:
            logger.warning("Invalid token provided - no user found")
            raise credentials_exception

        user_id = response.user.id
        user_email = response.user.email

        if not user_id or not user_email:
            logger.warning("Invalid user data in token")
            raise credentials_exception

        # Get user profile from Supabase
        try:
            profile_response = (
                supabase.table("profiles").select("*").eq("id", user_id).execute()
            )

            if profile_response.data and len(profile_response.data) > 0:
                # Profile exists, use profile data
                profile = profile_response.data[0]
                logger.debug(f"User profile found for: {user_email}")
                return {
                    "id": profile["id"],
                    "username": profile["username"],
                    "email": user_email,
                    "full_name": profile.get("full_name", ""),
                    "role": profile.get("role", "buyer"),
                    "is_verified_seller": profile.get("is_verified_seller", False),
                    "created_at": profile.get("created_at"),
                }
            else:
                # Profile doesn't exist, create a fallback user object
                logger.warning(f"Profile not found for user {user_id}, using auth data")
                username = response.user.user_metadata.get("username")
                if not username:
                    username = user_email.split("@")[0]

                return {
                    "id": user_id,
                    "username": username,
                    "email": user_email,
                    "full_name": response.user.user_metadata.get("full_name", ""),
                    "role": "buyer",
                    "is_verified_seller": False,
                    "created_at": response.user.created_at,
                }

        except Exception as profile_error:
            logger.error(f"Error fetching user profile: {profile_error}")
            # Fallback to auth data if profile fetch fails
            username = response.user.user_metadata.get("username")
            if not username:
                username = user_email.split("@")[0]

            return {
                "id": user_id,
                "username": username,
                "email": user_email,
                "full_name": response.user.user_metadata.get("full_name", ""),
                "role": "buyer",
                "is_verified_seller": False,
                "created_at": response.user.created_at,
            }

    except AuthApiError as e:
        logger.error(f"Supabase auth API error: {e}")
        error_message = str(e).lower()

        if "invalid token" in error_message or "expired" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired or is invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get the current active user with additional validation"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active (you can add more validation here)
    if not current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user data",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


async def require_admin_role(
    current_user: dict = Depends(get_current_active_user),
) -> dict:
    """Require admin role for the current user"""
    user_role = current_user.get("role")
    if user_role != "admin":
        logger.warning(
            f"Admin access denied for user {current_user.get('email')} with role {user_role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def require_seller_role(
    current_user: dict = Depends(get_current_active_user),
) -> dict:
    """Require seller role for the current user"""
    user_role = current_user.get("role")
    if user_role not in ["seller", "admin"]:
        logger.warning(
            f"Seller access denied for user {current_user.get('email')} with role {user_role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Seller access required"
        )
    return current_user


async def require_verified_seller(
    current_user: dict = Depends(get_current_active_user),
) -> dict:
    """Require verified seller status for the current user"""
    user_role = current_user.get("role")
    is_verified = current_user.get("is_verified_seller", False)

    if user_role not in ["seller", "admin"]:
        logger.warning(
            f"Seller access denied for user {current_user.get('email')} with role {user_role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Seller access required"
        )

    if not is_verified and user_role != "admin":
        logger.warning(
            f"Verified seller access denied for user {current_user.get('email')}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verified seller status required",
        )

    return current_user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[dict]:
    """Get current user if authenticated, otherwise return None (for optional auth)"""
    if not token:
        return None

    try:
        return await get_current_user(token)
    except HTTPException:
        return None
    except Exception:
        return None
