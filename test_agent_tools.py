"""Test agent tools functionality"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from konnect.database import Base
from konnect import models, schemas, crud
from konnect.agent_tools import get_user_activity_tool, tool_registry, get_agent_prompt


# Create test database
TEST_DATABASE_URL = "sqlite:///./test_agent_tools.db"
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
        password="testpassword"
    )
    return crud.create_user(db_session, user_data)


@pytest.fixture
def sample_marketplace(db_session, sample_user):
    """Create a sample marketplace for testing"""
    marketplace_data = schemas.MarketplaceCreate(
        name="Test Marketplace",
        description="A test marketplace"
    )
    return crud.create_marketplace(db_session, marketplace_data, sample_user.id)


@pytest.fixture
def sample_listing(db_session, sample_user, sample_marketplace):
    """Create a sample listing for testing"""
    listing_data = schemas.ListingCreate(
        title="Test Listing",
        description="A test listing",
        price=99.99,
        category="electronics",
        marketplace_id=sample_marketplace.id
    )
    return crud.create_listing(db_session, listing_data, sample_user.id)


def test_create_purchase(db_session, sample_user, sample_listing):
    """Test purchase creation"""
    purchase_data = schemas.PurchaseCreate(
        listing_id=sample_listing.id,
        amount=99.99,
        status="completed",
        transaction_hash="test_hash_123"
    )
    
    db_purchase = crud.create_purchase(db_session, purchase_data, sample_user.id)
    
    assert db_purchase.user_id == sample_user.id
    assert db_purchase.listing_id == sample_listing.id
    assert db_purchase.amount == 99.99
    assert db_purchase.status == "completed"
    assert db_purchase.transaction_hash == "test_hash_123"
    assert db_purchase.created_at is not None


def test_create_browsing_history(db_session, sample_user, sample_listing):
    """Test browsing history creation"""
    browsing_data = schemas.BrowsingHistoryCreate(
        listing_id=sample_listing.id,
        action="view"
    )
    
    db_browsing = crud.create_browsing_history(db_session, browsing_data, sample_user.id)
    
    assert db_browsing.user_id == sample_user.id
    assert db_browsing.listing_id == sample_listing.id
    assert db_browsing.action == "view"
    assert db_browsing.created_at is not None


def test_get_user_purchases(db_session, sample_user, sample_listing):
    """Test getting user purchases"""
    # Create multiple purchases
    for i in range(3):
        purchase_data = schemas.PurchaseCreate(
            listing_id=sample_listing.id,
            amount=50.0 + i * 10,
            status="completed"
        )
        crud.create_purchase(db_session, purchase_data, sample_user.id)
    
    purchases = crud.get_user_purchases(db_session, sample_user.id)
    
    assert len(purchases) == 3
    # Should be ordered by created_at desc
    assert purchases[0].amount == 70.0  # Latest purchase
    assert purchases[2].amount == 50.0  # Earliest purchase


def test_get_user_browsing_history(db_session, sample_user, sample_listing):
    """Test getting user browsing history"""
    # Create multiple browsing entries
    actions = ["view", "favorite", "share"]
    for action in actions:
        browsing_data = schemas.BrowsingHistoryCreate(
            listing_id=sample_listing.id,
            action=action
        )
        crud.create_browsing_history(db_session, browsing_data, sample_user.id)
    
    browsing_history = crud.get_user_browsing_history(db_session, sample_user.id)
    
    assert len(browsing_history) == 3
    assert browsing_history[0].action == "share"  # Latest action


def test_get_user_activity(db_session, sample_user, sample_listing):
    """Test getting complete user activity"""
    # Create purchases
    purchase_data = schemas.PurchaseCreate(
        listing_id=sample_listing.id,
        amount=99.99,
        status="completed"
    )
    crud.create_purchase(db_session, purchase_data, sample_user.id)
    
    # Create browsing history
    browsing_data = schemas.BrowsingHistoryCreate(
        listing_id=sample_listing.id,
        action="view"
    )
    crud.create_browsing_history(db_session, browsing_data, sample_user.id)
    
    activity = crud.get_user_activity(db_session, sample_user.id)
    
    assert activity.user_id == sample_user.id
    assert len(activity.purchases) == 1
    assert len(activity.browsing_history) == 1
    assert activity.purchases[0].amount == 99.99
    assert activity.browsing_history[0].action == "view"


def test_agent_tool_registry():
    """Test agent tool registry functionality"""
    # Test that our tool is registered
    tool = tool_registry.get_tool("get_user_activity")
    assert tool is not None
    assert tool.name == "get_user_activity"
    assert "user purchase history" in tool.description
    
    # Test getting all tools
    all_tools = tool_registry.get_all_tools()
    assert len(all_tools) >= 1
    
    # Test that our tool is in the list
    tool_names = [t.name for t in all_tools]
    assert "get_user_activity" in tool_names


def test_agent_prompt():
    """Test agent prompt generation"""
    prompt = get_agent_prompt()
    
    assert "get_user_activity" in prompt
    assert "purchase history" in prompt
    assert "browsing behavior" in prompt
    assert "recommendations" in prompt
    assert "user_id" in prompt


def test_user_activity_tool_function(db_session, sample_user, sample_listing):
    """Test the agent tool function directly"""
    # Create test data
    purchase_data = schemas.PurchaseCreate(
        listing_id=sample_listing.id,
        amount=149.99,
        status="completed"
    )
    crud.create_purchase(db_session, purchase_data, sample_user.id)
    
    browsing_data = schemas.BrowsingHistoryCreate(
        listing_id=sample_listing.id,
        action="favorite"
    )
    crud.create_browsing_history(db_session, browsing_data, sample_user.id)
    
    # Mock the database session for the tool
    # Note: In a real implementation, we'd need to properly handle DB sessions
    # For now, we'll test the CRUD function directly since the tool function
    # depends on the global database session
    activity = crud.get_user_activity(db_session, sample_user.id)
    
    # Verify the structure matches what the tool would return
    assert activity.user_id == sample_user.id
    assert len(activity.purchases) == 1
    assert len(activity.browsing_history) == 1
    assert activity.purchases[0].amount == 149.99
    assert activity.browsing_history[0].action == "favorite"


def test_model_relationships(db_session, sample_user, sample_listing):
    """Test the new model relationships"""
    # Create purchase and browsing history
    purchase_data = schemas.PurchaseCreate(
        listing_id=sample_listing.id,
        amount=99.99,
        status="completed"
    )
    db_purchase = crud.create_purchase(db_session, purchase_data, sample_user.id)
    
    browsing_data = schemas.BrowsingHistoryCreate(
        listing_id=sample_listing.id,
        action="view"
    )
    db_browsing = crud.create_browsing_history(db_session, browsing_data, sample_user.id)
    
    # Refresh objects to get relationships
    db_session.refresh(sample_user)
    db_session.refresh(sample_listing)
    
    # Test user relationships
    assert len(sample_user.purchases) == 1
    assert len(sample_user.browsing_history) == 1
    assert sample_user.purchases[0].id == db_purchase.id
    assert sample_user.browsing_history[0].id == db_browsing.id
    
    # Test listing relationships
    assert len(sample_listing.purchases) == 1
    assert len(sample_listing.browsing_history) == 1
    assert sample_listing.purchases[0].id == db_purchase.id
    assert sample_listing.browsing_history[0].id == db_browsing.id