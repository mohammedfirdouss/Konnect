"""Test configuration and fixtures"""

import os
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Set up mock Supabase environment variables for testing
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"

# Import after setting environment variables
from konnect.main import app


@pytest.fixture(scope="session")
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_supabase():
    """Mock Supabase client for testing"""
    mock_client = Mock()

    # Mock auth responses
    mock_user = Mock()
    mock_user.id = "test-user-id"
    mock_user.email = "test@example.com"
    mock_user.user_metadata = {"username": "testuser", "full_name": "Test User"}
    mock_user.created_at = "2023-01-01T00:00:00Z"

    mock_session = Mock()
    mock_session.access_token = "test-access-token"
    mock_session.refresh_token = "test-refresh-token"

    mock_auth_response = Mock()
    mock_auth_response.user = mock_user
    mock_auth_response.session = mock_session

    # Mock profile response
    mock_profile_response = Mock()
    mock_profile_response.data = [
        {
            "id": "test-user-id",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "buyer",
            "is_verified_seller": False,
            "created_at": "2023-01-01T00:00:00Z",
        }
    ]

    # Mock marketplace response
    mock_marketplace_response = Mock()
    mock_marketplace_response.data = {"id": 1, "name": "Test Marketplace"}

    # Mock listing response
    mock_listing_response = Mock()
    mock_listing_response.data = []

    mock_client.auth.sign_up.return_value = mock_auth_response
    mock_client.auth.sign_in_with_password.return_value = mock_auth_response
    mock_client.auth.get_user.return_value = Mock(user=mock_user)

    # Mock table operations
    mock_table = Mock()

    # Mock select operations
    mock_table.select.return_value.eq.return_value.execute.return_value = (
        mock_profile_response
    )
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_marketplace_response
    mock_table.select.return_value.limit.return_value.execute.return_value = (
        mock_listing_response
    )
    mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_marketplace_response
    mock_table.select.return_value.eq.return_value.range.return_value.execute.return_value = mock_listing_response

    # Mock insert operations
    mock_insert_response = Mock()
    mock_insert_response.data = [
        {
            "id": 1,
            "title": "Test Listing",
            "description": "A test listing",
            "price": 99.99,
            "category": "electronics",
            "marketplace_id": 1,
            "user_id": "test-user-id",
            "is_active": True,
        }
    ]
    mock_table.insert.return_value.execute.return_value = mock_insert_response

    # Mock update operations
    mock_update_response = Mock()
    mock_update_response.data = [{"id": 1}]
    mock_table.update.return_value.eq.return_value.execute.return_value = (
        mock_update_response
    )

    # Mock delete operations
    mock_delete_response = Mock()
    mock_delete_response.data = [{"id": 1}]
    mock_table.delete.return_value.eq.return_value.execute.return_value = (
        mock_delete_response
    )

    mock_client.table.return_value = mock_table

    with (
        patch("konnect.routers.auth.supabase", mock_client),
        patch("konnect.dependencies.supabase", mock_client),
        patch("konnect.supabase_client.supabase", mock_client),
        patch("konnect.routers.listings.supabase", mock_client),
        patch("konnect.routers.marketplaces.supabase", mock_client),
        patch("konnect.routers.users.supabase", mock_client),
        patch("konnect.routers.images.supabase", mock_client),
    ):
        yield mock_client
