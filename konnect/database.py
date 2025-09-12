"""Database configuration and session management"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Database URL configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./konnect.db"  # Default to SQLite for development
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    hashed_password = get_password_hash(user.password)
    db_user = UserInDB(
        id=user_id_counter,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True,
    )
    fake_users_db[user.username] = db_user
    user_id_counter += 1
    return db_user



def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
