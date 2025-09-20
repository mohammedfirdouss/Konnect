"""Test the database models functionality"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from konnect import crud, schemas
from konnect.database import Base

# Create test database
TEST_DATABASE_URL = "sqlite:///./test_konnect.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a database session for testing"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_user(db_session):
    """Test user creation"""
    user_data = schemas.UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="testpassword",
    )

    db_user = crud.create_user(db_session, user_data)

    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"
    assert db_user.full_name == "Test User"
    assert db_user.is_active is True
    assert db_user.created_at is not None
    assert hasattr(db_user, "hashed_password")


def test_create_marketplace(db_session):
    """Test marketplace creation"""
    # First create a user
    user_data = schemas.UserCreate(
        username="testuser", email="test@example.com", password="testpassword"
    )
    db_user = crud.create_user(db_session, user_data)

    # Then create a marketplace
    marketplace_data = schemas.MarketplaceCreate(
        name="Test Marketplace", description="A test marketplace"
    )

    db_marketplace = crud.create_marketplace(db_session, marketplace_data, db_user.id)

    assert db_marketplace.name == "Test Marketplace"
    assert db_marketplace.description == "A test marketplace"
    assert db_marketplace.created_by == db_user.id
    assert db_marketplace.is_active is True


def test_create_listing(db_session):
    """Test listing creation"""
    # Create user and marketplace first
    user_data = schemas.UserCreate(
        username="testuser", email="test@example.com", password="testpassword"
    )
    db_user = crud.create_user(db_session, user_data)

    marketplace_data = schemas.MarketplaceCreate(
        name="Test Marketplace", description="A test marketplace"
    )
    db_marketplace = crud.create_marketplace(db_session, marketplace_data, db_user.id)

    # Create listing
    listing_data = schemas.ListingCreate(
        title="Test Listing",
        description="A test listing",
        price=99.99,
        category="electronics",
        marketplace_id=db_marketplace.id,
    )

    db_listing = crud.create_listing(db_session, listing_data, db_user.id)

    assert db_listing.title == "Test Listing"
    assert db_listing.description == "A test listing"
    assert db_listing.price == 99.99
    assert db_listing.category == "electronics"
    assert db_listing.marketplace_id == db_marketplace.id
    assert db_listing.user_id == db_user.id
    assert db_listing.is_active is True


def test_user_relationships(db_session):
    """Test relationships between models"""
    # Create user
    user_data = schemas.UserCreate(
        username="testuser", email="test@example.com", password="testpassword"
    )
    db_user = crud.create_user(db_session, user_data)

    # Create marketplace
    marketplace_data = schemas.MarketplaceCreate(
        name="Test Marketplace", description="A test marketplace"
    )
    db_marketplace = crud.create_marketplace(db_session, marketplace_data, db_user.id)

    # Create listing
    listing_data = schemas.ListingCreate(
        title="Test Listing",
        description="A test listing",
        price=99.99,
        marketplace_id=db_marketplace.id,
    )
    db_listing = crud.create_listing(db_session, listing_data, db_user.id)

    # Test relationships
    assert len(db_user.marketplaces) == 1
    assert db_user.marketplaces[0].name == "Test Marketplace"

    assert len(db_user.listings) == 1
    assert db_user.listings[0].title == "Test Listing"

    assert len(db_marketplace.listings) == 1
    assert db_marketplace.listings[0].title == "Test Listing"

    assert db_listing.user.username == "testuser"
    assert db_listing.marketplace.name == "Test Marketplace"
