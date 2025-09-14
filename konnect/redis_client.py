"""Redis client configuration for caching recommendations"""

import os
import json
from typing import List, Optional
import redis
from redis.exceptions import ConnectionError, TimeoutError

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_EXPIRE_TIME = int(os.getenv("REDIS_EXPIRE_TIME", "3600"))  # 1 hour default


class RedisClient:
    """Redis client for caching recommendation data"""
    
    def __init__(self, url: str = REDIS_URL):
        """Initialize Redis client"""
        try:
            self.client = redis.from_url(url, decode_responses=True, socket_timeout=5)
            # Test connection
            self.client.ping()
        except (ConnectionError, TimeoutError):
            # In development/testing, use a mock client that stores data in memory
            self.client = MockRedisClient()
    
    def get_user_recommendations(self, user_id: int) -> Optional[List[int]]:
        """Get cached recommendations for a user
        
        Args:
            user_id: The user ID to get recommendations for
            
        Returns:
            List of listing IDs or None if not found
        """
        try:
            key = f"recommendations:user:{user_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None
    
    def set_user_recommendations(self, user_id: int, listing_ids: List[int]) -> bool:
        """Cache recommendations for a user
        
        Args:
            user_id: The user ID to cache recommendations for
            listing_ids: List of recommended listing IDs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            key = f"recommendations:user:{user_id}"
            data = json.dumps(listing_ids)
            self.client.setex(key, REDIS_EXPIRE_TIME, data)
            return True
        except Exception:
            return False
    
    def delete_user_recommendations(self, user_id: int) -> bool:
        """Delete cached recommendations for a user
        
        Args:
            user_id: The user ID to delete recommendations for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            key = f"recommendations:user:{user_id}"
            self.client.delete(key)
            return True
        except Exception:
            return False


class MockRedisClient:
    """Mock Redis client for testing and development when Redis is not available"""
    
    def __init__(self):
        self._data = {}
    
    def ping(self):
        """Mock ping method"""
        return True
    
    def get(self, key: str) -> Optional[str]:
        """Mock get method"""
        return self._data.get(key)
    
    def setex(self, key: str, timeout: int, value: str) -> bool:
        """Mock setex method"""
        self._data[key] = value
        return True
    
    def delete(self, key: str) -> int:
        """Mock delete method"""
        if key in self._data:
            del self._data[key]
            return 1
        return 0


# Global Redis client instance
redis_client = RedisClient()