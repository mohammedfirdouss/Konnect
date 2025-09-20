"""FastAPI dependencies for authentication using Supabase"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from . import crud
from .database import get_db
from .schemas import User
from .supabase_client import supabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from Supabase token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        response = supabase.auth.get_user(token)
        if not response.user:
            raise credentials_exception

        # The user object from Supabase has the user's ID.
        # We can use this ID to get the user's profile from our database.
        user_id = response.user.id
        user = crud.get_user(db, user_id=UUID(user_id))
        if user is None:
            # This case can happen if a user is deleted from the profiles table but still has a valid token.
            raise credentials_exception

        return User.model_validate(user)

    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user"""
    # Supabase handles user activation (e.g. email confirmation).
    # You can add more checks here if needed, for example, if you have a `is_active` flag in your `profiles` table.
    return current_user


async def require_admin_role(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require admin role for the current user"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def require_seller_role(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require seller role for the current user"""
    if current_user.role not in ["seller", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Seller access required"
        )
    return current_user
