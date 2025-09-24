"""Authentication router using Supabase"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..supabase_client import supabase
from ..schemas import UserCreate, Token
from ..dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register")
async def register_user(user: UserCreate):
    """Register a new user with Supabase"""
    if supabase is None:
        logger.error("Supabase client not configured for registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not configured. Please check environment variables."
        )
    
    try:
        logger.info(f"Attempting to register user: {user.email}")
        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
                "options": {
                    "data": {"username": user.username, "full_name": user.full_name}
                },
            }
        )
        
        if response.user:
            logger.info(f"User registered successfully: {response.user.id}")
            return {
                "message": "User registered successfully",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "username": response.user.user_metadata.get("username"),
                    "full_name": response.user.user_metadata.get("full_name"),
                }
            }
        else:
            logger.warning(f"Registration failed for {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not register user",
            )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token from Supabase"""
    if supabase is None:
        logger.error("Supabase client not configured for login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not configured. Please check environment variables."
        )
    
    try:
        logger.info(f"Attempting login for: {form_data.username}")
        response = supabase.auth.sign_in_with_password(
            {"email": form_data.username, "password": form_data.password}
        )
        
        if response.session:
            logger.info(f"Login successful for: {form_data.username}")
            return Token(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
            )
        else:
            logger.warning(f"Login failed for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/health")
async def auth_health_check():
    """Check authentication service health"""
    from ..supabase_client import check_supabase_connection
    
    connection_status = check_supabase_connection()
    
    if connection_status["supabase_configured"]:
        return {
            "status": "healthy",
            "service": "authentication",
            "supabase_status": connection_status
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not properly configured"
        )
