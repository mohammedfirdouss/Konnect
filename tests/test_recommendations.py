"""Tests for the recommendations endpoint"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from konnect.redis_client import redis_client
from konnect.tasks import generate_recommendations_now
from konnect.routers.users import router as users_router
from konnect.schemas import RecommendationResponse

# Create a test app with just the users router for isolated testing
test_app = FastAPI()
test_app.include_router(users_router)

client = TestClient(test_app)


class TestRecommendationsEndpoint:
    """Test cases for the recommendations endpoint"""
    
    def test_get_recommendations_no_auth(self):
        """Test that the endpoint requires authentication"""
        response = client.get("/users/me/recommendations")
        assert response.status_code == 401
    
    def test_recommendation_response_schema(self):
        """Test that the RecommendationResponse schema works correctly"""
        from datetime import datetime
        
        # Test schema validation
        response_data = {
            "user_id": 1,
            "listing_ids": [1, 2, 3, 4, 5],
            "cached_at": datetime.utcnow(),
            "expires_at": datetime.utcnow()
        }
        
        response = RecommendationResponse(**response_data)
        assert response.user_id == 1
        assert response.listing_ids == [1, 2, 3, 4, 5]
        assert response.cached_at is not None
        assert response.expires_at is not None


class TestRecommendationGeneration:
    """Test cases for recommendation generation"""
    
    def test_generate_recommendations_now(self):
        """Test manual recommendation generation"""
        user_id = 1
        
        # Generate recommendations
        success = generate_recommendations_now(user_id)
        assert success is True
        
        # Check that recommendations were cached
        cached_recommendations = redis_client.get_user_recommendations(user_id)
        assert cached_recommendations is not None
        assert isinstance(cached_recommendations, list)
        assert len(cached_recommendations) == 5
        assert all(isinstance(item, int) for item in cached_recommendations)
    
    def test_recommendation_caching(self):
        """Test that recommendations can be cached and retrieved"""
        user_id = 2
        test_recommendations = [10, 20, 30, 40, 50]
        
        # Cache recommendations
        success = redis_client.set_user_recommendations(user_id, test_recommendations)
        assert success is True
        
        # Retrieve recommendations
        cached_recommendations = redis_client.get_user_recommendations(user_id)
        assert cached_recommendations == test_recommendations
        
        # Delete recommendations
        success = redis_client.delete_user_recommendations(user_id)
        assert success is True
        
        # Verify deleted
        cached_recommendations = redis_client.get_user_recommendations(user_id)
        assert cached_recommendations is None
    
    def test_redis_client_fallback(self):
        """Test that Redis client works with mock fallback"""
        # Test that our mock Redis client works when Redis is not available
        from konnect.redis_client import MockRedisClient
        
        mock_client = MockRedisClient()
        
        # Test ping
        assert mock_client.ping() is True
        
        # Test set and get
        mock_client.setex("test:key", 3600, "test_value")
        assert mock_client.get("test:key") == "test_value"
        
        # Test delete
        deleted = mock_client.delete("test:key")
        assert deleted == 1
        assert mock_client.get("test:key") is None
    
    def test_mock_recommendation_agent(self):
        """Test the mock recommendation agent function"""
        from konnect.tasks import mock_recommendation_agent
        
        # Test different user IDs get different recommendations
        recommendations_1 = mock_recommendation_agent(1)
        recommendations_2 = mock_recommendation_agent(2)
        
        assert len(recommendations_1) == 5
        assert len(recommendations_2) == 5
        assert all(isinstance(item, int) for item in recommendations_1)
        assert all(isinstance(item, int) for item in recommendations_2)
        
        # Different users should get different recommendations
        assert recommendations_1 != recommendations_2


class TestCeleryTaskConfiguration:
    """Test cases for Celery task configuration"""
    
    def test_celery_app_configuration(self):
        """Test that Celery app is configured correctly"""
        from konnect.tasks import celery_app
        
        # Test basic configuration
        assert celery_app.main == "konnect_recommendations"
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.timezone == "UTC"
        
        # Test beat schedule exists
        assert "generate-recommendations" in celery_app.conf.beat_schedule


if __name__ == "__main__":
    pytest.main([__file__, "-v"])