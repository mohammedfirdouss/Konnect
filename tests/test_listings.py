"""Tests for listings CRUD endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from konnect import models
from konnect.database import Base, get_db
from konnect.main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_listings.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Reset database before each test"""
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user and return authentication token"""
    db = TestingSessionLocal()
    try:
        # Create user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        }

        # Register user
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200

        # Login to get token
        login_data = {"username": "testuser", "password": "testpassword123"}
        response = client.post("/auth/token", data=login_data)
        assert response.status_code == 200

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        return {"headers": headers, "user_id": response.json().get("user_id", 1)}
    finally:
        db.close()


@pytest.fixture
def test_marketplace(test_user):
    """Create a test marketplace"""
    db = TestingSessionLocal()
    try:
        marketplace = models.Marketplace(
            name="Test Marketplace",
            description="A marketplace for testing",
            created_by=1,  # Assuming first user has ID 1
        )
        db.add(marketplace)
        db.commit()
        db.refresh(marketplace)
        return marketplace
    finally:
        db.close()


def test_create_listing_success(test_user, test_marketplace):
    """Test creating a listing successfully"""
    listing_data = {
        "title": "Test Listing",
        "description": "A test listing",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": test_marketplace.id,
    }

    response = client.post(
        "/listings/", json=listing_data, headers=test_user["headers"]
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Listing"
    assert data["price"] == 99.99
    assert data["category"] == "electronics"
    assert data["marketplace_id"] == test_marketplace.id
    assert data["is_active"] is True


def test_create_listing_unauthorized():
    """Test creating a listing without authentication"""
    listing_data = {
        "title": "Test Listing",
        "description": "A test listing",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": 1,
    }

    response = client.post("/listings/", json=listing_data)
    assert response.status_code == 401


def test_create_listing_invalid_marketplace(test_user):
    """Test creating a listing with invalid marketplace"""
    listing_data = {
        "title": "Test Listing",
        "description": "A test listing",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": 999,  # Non-existent marketplace
    }

    response = client.post(
        "/listings/", json=listing_data, headers=test_user["headers"]
    )
    assert response.status_code == 404
    assert "Marketplace not found" in response.json()["detail"]


def test_get_listings_empty():
    """Test getting listings when none exist"""
    response = client.get("/listings/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_listings_with_data(test_user, test_marketplace):
    """Test getting listings with data"""
    # Create a test listing first
    listing_data = {
        "title": "Test Listing",
        "description": "A test listing",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": test_marketplace.id,
    }

    create_response = client.post(
        "/listings/", json=listing_data, headers=test_user["headers"]
    )
    assert create_response.status_code == 201

    # Now get all listings
    response = client.get("/listings/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Test Listing"


def test_get_listings_with_filters(test_user, test_marketplace):
    """Test getting listings with marketplace and category filters"""
    # Create test listings
    listing1_data = {
        "title": "Electronics Item",
        "description": "An electronics item",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": test_marketplace.id,
    }

    listing2_data = {
        "title": "Book Item",
        "description": "A book item",
        "price": 19.99,
        "category": "books",
        "marketplace_id": test_marketplace.id,
    }

    client.post("/listings/", json=listing1_data, headers=test_user["headers"])
    client.post("/listings/", json=listing2_data, headers=test_user["headers"])

    # Test marketplace filter
    response = client.get(f"/listings/?marketplace_id={test_marketplace.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Test category filter
    response = client.get("/listings/?category=electronics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(item["category"] == "electronics" for item in data)


def test_get_listing_by_id(test_user, test_marketplace):
    """Test getting a single listing by ID"""
    # Create a test listing first
    listing_data = {
        "title": "Test Listing",
        "description": "A test listing",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": test_marketplace.id,
    }

    create_response = client.post(
        "/listings/", json=listing_data, headers=test_user["headers"]
    )
    listing_id = create_response.json()["id"]

    # Get the listing by ID
    response = client.get(f"/listings/{listing_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == listing_id
    assert data["title"] == "Test Listing"


def test_get_listing_not_found():
    """Test getting a listing that doesn't exist"""
    response = client.get("/listings/999")
    assert response.status_code == 404
    assert "Listing not found" in response.json()["detail"]


def test_update_listing_success(test_user, test_marketplace):
    """Test updating a listing successfully"""
    # Create a test listing first
    listing_data = {
        "title": "Original Title",
        "description": "Original description",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": test_marketplace.id,
    }

    create_response = client.post(
        "/listings/", json=listing_data, headers=test_user["headers"]
    )
    listing_id = create_response.json()["id"]

    # Update the listing
    update_data = {"title": "Updated Title", "price": 199.99}

    response = client.put(
        f"/listings/{listing_id}", json=update_data, headers=test_user["headers"]
    )
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["price"] == 199.99
    assert data["description"] == "Original description"  # Unchanged


def test_update_listing_unauthorized(test_user, test_marketplace):
    """Test updating a listing without proper authorization"""
    # Create a test listing first
    listing_data = {
        "title": "Test Listing",
        "description": "A test listing",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": test_marketplace.id,
    }

    create_response = client.post(
        "/listings/", json=listing_data, headers=test_user["headers"]
    )
    listing_id = create_response.json()["id"]

    # Try to update without authentication
    update_data = {"title": "Hacked Title"}
    response = client.put(f"/listings/{listing_id}", json=update_data)
    assert response.status_code == 401


def test_update_listing_not_found(test_user):
    """Test updating a listing that doesn't exist"""
    update_data = {"title": "Updated Title"}
    response = client.put(
        "/listings/999", json=update_data, headers=test_user["headers"]
    )
    assert response.status_code == 404


def test_delete_listing_success(test_user, test_marketplace):
    """Test deleting a listing successfully"""
    # Create a test listing first
    listing_data = {
        "title": "Test Listing",
        "description": "A test listing",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": test_marketplace.id,
    }

    create_response = client.post(
        "/listings/", json=listing_data, headers=test_user["headers"]
    )
    listing_id = create_response.json()["id"]

    # Delete the listing
    response = client.delete(f"/listings/{listing_id}", headers=test_user["headers"])
    assert response.status_code == 204

    # Verify the listing is no longer accessible
    get_response = client.get(f"/listings/{listing_id}")
    assert get_response.status_code == 404


def test_delete_listing_unauthorized(test_user, test_marketplace):
    """Test deleting a listing without proper authorization"""
    # Create a test listing first
    listing_data = {
        "title": "Test Listing",
        "description": "A test listing",
        "price": 99.99,
        "category": "electronics",
        "marketplace_id": test_marketplace.id,
    }

    create_response = client.post(
        "/listings/", json=listing_data, headers=test_user["headers"]
    )
    listing_id = create_response.json()["id"]

    # Try to delete without authentication
    response = client.delete(f"/listings/{listing_id}")
    assert response.status_code == 401


def test_delete_listing_not_found(test_user):
    """Test deleting a listing that doesn't exist"""
    response = client.delete("/listings/999", headers=test_user["headers"])
    assert response.status_code == 404


def test_pagination(test_user, test_marketplace):
    """Test pagination functionality"""
    # Create multiple test listings
    for i in range(5):
        listing_data = {
            "title": f"Test Listing {i}",
            "description": f"Test listing number {i}",
            "price": 10.0 + i,
            "category": "test",
            "marketplace_id": test_marketplace.id,
        }
        client.post("/listings/", json=listing_data, headers=test_user["headers"])

    # Test pagination
    response = client.get("/listings/?skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3

    response = client.get("/listings/?skip=3&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3
