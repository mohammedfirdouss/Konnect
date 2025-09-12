"""In-memory database for users"""

from typing import Dict, Optional

from .auth import get_password_hash
from .models import UserCreate, UserInDB

# In-memory user database
fake_users_db: Dict[str, UserInDB] = {}
user_id_counter = 1


def get_user(username: str) -> Optional[UserInDB]:
    """Get user by username"""
    return fake_users_db.get(username)


def create_user(user: UserCreate) -> UserInDB:
    """Create a new user"""
    global user_id_counter

    hashed_password = get_password_hash(user.password)
    db_user = UserInDB(
        id=user_id_counter,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    fake_users_db[user.username] = db_user
    user_id_counter += 1
    return db_user


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user"""
    from .auth import verify_password

    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
