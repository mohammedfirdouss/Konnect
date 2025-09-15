"""FastAPI dependencies for authentication"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import crud
from .auth import verify_token
from .database import get_db
from .schemas import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return User.model_validate(user)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
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
