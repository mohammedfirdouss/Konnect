"""Authentication utilities and error handling"""

import re
import logging
from typing import Tuple
from fastapi import HTTPException, status
from supabase import AuthApiError, AuthInvalidCredentialsError

logger = logging.getLogger(__name__)


def validate_email_format(email: str) -> Tuple[bool, str]:
    """Validate email format and return (is_valid, error_message)"""
    if not email:
        return False, "Email is required"

    email = email.strip().lower()

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        return False, "Invalid email format"

    if len(email) > 254:  # RFC 5321 limit
        return False, "Email address is too long"

    return True, ""


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password strength and return (is_valid, error_message)"""
    if not password:
        return False, "Password is required"

    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    # Check for common weak passwords
    weak_passwords = [
        "password",
        "123456",
        "123456789",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
    ]

    if password.lower() in weak_passwords:
        return False, "Password is too common, please choose a stronger password"

    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format and return (is_valid, error_message)"""
    if not username:
        return False, "Username is required"

    username = username.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 30:
        return False, "Username must be less than 30 characters"

    # Allow letters, numbers, underscores, and hyphens
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return (
            False,
            "Username can only contain letters, numbers, underscores, and hyphens",
        )

    # Cannot start or end with underscore or hyphen
    if username.startswith(("_", "-")) or username.endswith(("_", "-")):
        return False, "Username cannot start or end with underscore or hyphen"

    return True, ""


def handle_auth_error(
    error: Exception, operation: str = "authentication"
) -> HTTPException:
    """Handle authentication errors and return appropriate HTTP exceptions"""
    logger.error(f"Auth error during {operation}: {error}")

    if isinstance(error, AuthInvalidCredentialsError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if isinstance(error, AuthApiError):
        error_message = str(error).lower()

        if "email not confirmed" in error_message:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please confirm your email address before logging in",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif (
            "already registered" in error_message
            or "user already exists" in error_message
        ):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        elif "password" in error_message:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet requirements",
            )
        elif "invalid token" in error_message or "expired" in error_message:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired or is invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication error: {str(error)}",
            )

    # Generic error handling
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal server error during {operation}",
    )


def sanitize_user_input(input_string: str, max_length: int = 255) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""

    # Remove leading/trailing whitespace
    sanitized = input_string.strip()

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', "", sanitized)

    return sanitized


def create_user_response(user_data: dict) -> dict:
    """Create a standardized user response object"""
    return {
        "id": user_data.get("id"),
        "email": user_data.get("email"),
        "username": user_data.get("username"),
        "full_name": user_data.get("full_name", ""),
        "role": user_data.get("role", "buyer"),
        "is_verified_seller": user_data.get("is_verified_seller", False),
        "created_at": user_data.get("created_at"),
    }


def log_auth_event(event_type: str, user_email: str, success: bool, details: str = ""):
    """Log authentication events for security monitoring"""
    status = "SUCCESS" if success else "FAILURE"
    logger.info(f"AUTH_EVENT: {event_type} - {status} - User: {user_email} - {details}")


def validate_token_format(token: str) -> bool:
    """Validate JWT token format"""
    if not token:
        return False

    # JWT tokens have 3 parts separated by dots
    parts = token.split(".")
    if len(parts) != 3:
        return False

    # Each part should be base64 encoded
    try:
        for part in parts:
            if not part:
                return False
            # Basic base64 validation
            import base64

            base64.b64decode(part + "==")  # Add padding if needed
    except Exception:
        return False

    return True
