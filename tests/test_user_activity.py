"""Test the user activity functionality and agent tool integration"""

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from konnect import crud, schemas
from konnect.agents.recommendation import (
    RecommendationAgent,
    get_user_activity_with_db,
)
from konnect.database import Base

# Create test database
TEST_DATABASE_URL = "sqlite:///./test_user_activity.db"
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


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user_data = schemas.UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="testpassword",
    )
    return crud.create_user(db_session, user_data)


@pytest.fixture
def sample_marketplace(db_session, sample_user):
    """Create a sample marketplace for testing"""
    marketplace_data = schemas.MarketplaceCreate(
        name="Test Marketplace", description="A test marketplace"
    )
    return crud.create_marketplace(db_session, marketplace_data, sample_user.id)


@pytest.fixture
def sample_listing(db_session, sample_user, sample_marketplace):
    """Create a sample listing for testing"""
    listing_data = schemas.ListingCreate(
        title="Test Laptop",
        description="A great laptop for students",
        price=500.0,
        category="Electronics",
        marketplace_id=sample_marketplace.id,
    )
    return crud.create_listing(db_session, listing_data, sample_user.id)


def test_create_purchase(db_session, sample_user, sample_listing):
    """Test purchase creation"""
    purchase_data = schemas.PurchaseCreate(
        listing_id=sample_listing.id, amount=500.0, payment_method="solana"
    )

    db_purchase = crud.create_purchase(db_session, purchase_data, sample_user.id)

    assert db_purchase.user_id == sample_user.id
    assert db_purchase.listing_id == sample_listing.id
    assert db_purchase.amount == 500.0
    assert db_purchase.payment_method == "solana"
    assert db_purchase.status == "pending"
    assert db_purchase.created_at is not None


def test_create_user_activity(db_session, sample_user, sample_listing):
    """Test user activity creation"""
    activity_data = schemas.UserActivityCreate(
        activity_type="view",
        target_id=sample_listing.id,
        target_type="listing",
        activity_data=json.dumps({"duration": 30, "source": "search"}),
    )

    db_activity = crud.create_user_activity(db_session, activity_data, sample_user.id)

    assert db_activity.user_id == sample_user.id
    assert db_activity.activity_type == "view"
    assert db_activity.target_id == sample_listing.id
    assert db_activity.target_type == "listing"
    assert db_activity.activity_data is not None
    assert db_activity.created_at is not None


def test_get_user_activities(db_session, sample_user, sample_listing):
    """Test retrieving user activities"""
    # Create multiple activities
    for i in range(3):
        activity_data = schemas.UserActivityCreate(
            activity_type="view",
            target_id=sample_listing.id,
            target_type="listing",
            activity_data=json.dumps({"view_number": i}),
        )
        crud.create_user_activity(db_session, activity_data, sample_user.id)

    activities = crud.get_user_activities(db_session, sample_user.id)

    assert len(activities) == 3
    assert all(a.user_id == sample_user.id for a in activities)
    assert all(a.activity_type == "view" for a in activities)


def test_get_user_purchases(db_session, sample_user, sample_listing):
    """Test retrieving user purchases"""
    # Create multiple purchases
    for i in range(2):
        purchase_data = schemas.PurchaseCreate(
            listing_id=sample_listing.id,
            amount=100.0 * (i + 1),
            payment_method="solana",
        )
        purchase = crud.create_purchase(db_session, purchase_data, sample_user.id)
        if i == 0:
            purchase.status = "completed"
            db_session.commit()

    purchases = crud.get_user_purchases(db_session, sample_user.id)

    assert len(purchases) == 2
    assert all(p.user_id == sample_user.id for p in purchases)
    assert purchases[0].amount == 200.0  # Most recent first
    assert purchases[1].amount == 100.0


def test_get_user_activity_summary(db_session, sample_user, sample_listing):
    """Test comprehensive user activity summary"""
    # Create a completed purchase
    purchase_data = schemas.PurchaseCreate(
        listing_id=sample_listing.id, amount=500.0, payment_method="solana"
    )
    purchase = crud.create_purchase(db_session, purchase_data, sample_user.id)
    purchase.status = "completed"
    db_session.commit()

    # Create some activities
    activity_data = schemas.UserActivityCreate(
        activity_type="view",
        target_id=sample_listing.id,
        target_type="listing",
        activity_data=json.dumps({"source": "search"}),
    )
    crud.create_user_activity(db_session, activity_data, sample_user.id)

    search_data = schemas.UserActivityCreate(
        activity_type="search",
        target_id=None,
        target_type=None,
        activity_data=json.dumps({"query": "laptop"}),
    )
    crud.create_user_activity(db_session, search_data, sample_user.id)

    summary = crud.get_user_activity_summary(db_session, sample_user.id)

    assert summary["user_id"] == sample_user.id
    assert summary["total_purchases"] == 1
    assert summary["total_spent"] == 500.0
    assert len(summary["recent_purchases"]) == 1
    assert len(summary["recent_activities"]) == 2
    assert "Electronics" in summary["favorite_categories"]
    assert len(summary["recent_views"]) == 1
    assert len(summary["recent_searches"]) == 1


def test_get_user_activity_function(db_session, sample_user, sample_listing):
    """Test the get_user_activity function that the agent uses"""
    # Create test data
    purchase_data = schemas.PurchaseCreate(
        listing_id=sample_listing.id, amount=300.0, payment_method="solana"
    )
    purchase = crud.create_purchase(db_session, purchase_data, sample_user.id)
    purchase.status = "completed"
    db_session.commit()

    activity_data = schemas.UserActivityCreate(
        activity_type="view", target_id=sample_listing.id, target_type="listing"
    )
    crud.create_user_activity(db_session, activity_data, sample_user.id)

    # Test the function with the test database session
    result = get_user_activity_with_db(db_session, sample_user.id)

    assert result["user_id"] == sample_user.id
    assert result["total_purchases"] == 1
    assert result["total_spent"] == 300.0
    assert len(result["recent_purchases"]) == 1
    assert len(result["recent_activities"]) == 1
    assert result["recent_purchases"][0]["amount"] == 300.0
    assert result["recent_activities"][0]["activity_type"] == "view"


def test_recommendation_agent_initialization():
    """Test that the recommendation agent initializes correctly"""
    agent = RecommendationAgent()

    # Should not raise an exception
    assert agent is not None

    # Test that it can handle queries (even in mock mode)
    response = agent.get_recommendations("I need a laptop for studying")
    assert isinstance(response, str)
    assert len(response) > 0


def test_personalized_recommendations():
    """Test personalized recommendations method"""
    agent = RecommendationAgent()

    response = agent.get_personalized_recommendations(1, "I need study materials")
    assert isinstance(response, str)
    assert len(response) > 0


def test_user_relationships(db_session, sample_user, sample_listing):
    """Test that relationships work correctly with new models"""
    # Create purchase and activity
    purchase_data = schemas.PurchaseCreate(
        listing_id=sample_listing.id, amount=200.0, payment_method="solana"
    )
    crud.create_purchase(db_session, purchase_data, sample_user.id)

    activity_data = schemas.UserActivityCreate(
        activity_type="view", target_id=sample_listing.id, target_type="listing"
    )
    crud.create_user_activity(db_session, activity_data, sample_user.id)

    # Test relationships
    db_session.refresh(sample_user)
    assert len(sample_user.purchases) == 1
    assert len(sample_user.activities) == 1
    assert sample_user.purchases[0].amount == 200.0
    assert sample_user.activities[0].activity_type == "view"

    # Test listing relationships
    db_session.refresh(sample_listing)
    assert len(sample_listing.purchases) == 1
    assert sample_listing.purchases[0].user_id == sample_user.id
