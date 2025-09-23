"""Authentication router using Supabase"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..supabase_client import supabase
from ..schemas import User, UserCreate, Token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    """Register a new user with Supabase"""
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not configured. Please check environment variables."
        )
    
    try:
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
            # The trigger in the database will create a profile, so we just return the user data
            return User(
                id=response.user.id,
                username=response.user.user_metadata.get("username"),
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name"),
                created_at=response.user.created_at,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.get("message", "Could not register user"),
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token from Supabase"""
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not configured. Please check environment variables."
        )
    
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": form_data.username, "password": form_data.password}
        )
        if response.session:
            return Token(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response.get("message", "Incorrect email or password"),
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
