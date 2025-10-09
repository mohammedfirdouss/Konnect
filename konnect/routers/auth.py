"""Authentication router using Supabase"""

import logging
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from supabase import AuthApiError, AuthInvalidCredentialsError
from pydantic import BaseModel, EmailStr, validator

from ..supabase_client import supabase
from ..schemas import Token
from ..dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request model with validation"""

    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class RegisterRequest(BaseModel):
    """Registration request model with validation"""

    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = ""

    @validator("username")
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


def validate_email_format(email: str) -> bool:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    return True, ""


@router.post("/register")
async def register_user(user: RegisterRequest):
    """Register a new user with Supabase with comprehensive validation"""
    if supabase is None:
        logger.error("Supabase client not configured for registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured. Please check environment variables.",
        )

    # Validate email format
    if not validate_email_format(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    # Validate password strength
    is_valid_password, password_error = validate_password_strength(user.password)
    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error,
        )

    try:
        logger.info(f"Attempting to register user: {user.email}")

        # Check if user already exists
        try:
            supabase.auth.sign_in_with_password(
                {"email": user.email, "password": "dummy_password_to_check_existence"}
            )
            # If we get here, user exists
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        except AuthInvalidCredentialsError:
            # User doesn't exist, continue with registration
            pass
        except Exception:
            # Other error, continue with registration
            pass

        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
                "options": {
                    "data": {
                        "username": user.username,
                        "full_name": user.full_name or "",
                    }
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
                },
            }
        else:
            logger.warning(f"Registration failed for {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not register user. Please try again.",
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except AuthApiError as e:
        logger.error(f"Supabase auth API error during registration: {e}")
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        elif "password" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet requirements",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed - please check your information",
            )
    except Exception as e:
        logger.error(f"Unexpected registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token from Supabase (OAuth2 compatible endpoint)"""
    if supabase is None:
        logger.error("Supabase client not configured for login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured. Please check environment variables.",
        )

    # Validate input
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    # Note: OAuth2PasswordRequestForm uses 'username' field but expects email value
    email = form_data.username.strip().lower()

    # Validate email format
    if not validate_email_format(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    try:
        logger.info(f"Attempting login for: {email}")
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": form_data.password}
        )

        if response.session:
            logger.info(f"Login successful for: {email}")
            return Token(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
            )
        else:
            logger.warning(f"Login failed for: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except AuthInvalidCredentialsError:
        logger.warning(f"Invalid credentials for: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AuthApiError as e:
        logger.error(f"Supabase auth API error: {e}")
        error_message = str(e)
        if "email not confirmed" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please confirm your email address before logging in",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"Unexpected login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@router.post("/login", response_model=Token)
async def login_with_email(
    email: str = Form(..., description="User email address"),
    password: str = Form(..., description="User password"),
):
    """Login with explicit email field (recommended endpoint)"""
    if supabase is None:
        logger.error("Supabase client not configured for login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured. Please check environment variables.",
        )

    # Validate input
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    email = email.strip().lower()

    # Validate email format
    if not validate_email_format(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    try:
        logger.info(f"Attempting login for: {email}")
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if response.session:
            logger.info(f"Login successful for: {email}")
            return Token(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
            )
        else:
            logger.warning(f"Login failed for: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except AuthInvalidCredentialsError:
        logger.warning(f"Invalid credentials for: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AuthApiError as e:
        logger.error(f"Supabase auth API error: {e}")
        error_message = str(e)
        if "email not confirmed" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please confirm your email address before logging in",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"Unexpected login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Form(...)):
    """Refresh access token using refresh token"""
    if supabase is None:
        logger.error("Supabase client not configured for token refresh")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured",
        )

    try:
        response = supabase.auth.refresh_session(refresh_token)

        if response.session:
            logger.info("Token refreshed successfully")
            return Token(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except AuthApiError as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh",
        )


@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout current user"""
    if supabase is None:
        logger.error("Supabase client not configured for logout")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured",
        )

    try:
        # Note: Supabase handles logout on the client side
        # This endpoint is mainly for logging purposes
        logger.info(f"User logged out: {current_user.get('email')}")
        return {"message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout",
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
            "supabase_status": connection_status,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not properly configured",
        )
