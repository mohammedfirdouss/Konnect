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
    
    mock_client.auth.sign_up.return_value = mock_auth_response
    mock_client.auth.sign_in_with_password.return_value = mock_auth_response
    mock_client.auth.get_user.return_value = Mock(user=mock_user)
    
    with patch('konnect.routers.auth.supabase', mock_client), \
         patch('konnect.dependencies.supabase', mock_client):
        yield mock_client