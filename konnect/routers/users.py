"""Users router"""

from fastapi import APIRouter, Depends
from ..models import User
from ..dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user