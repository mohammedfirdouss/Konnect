"""Redis client for caching user recommendations and other data"""

import json
import os
from typing import Any, List, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class MockRedisClient:
    """Mock Redis client for when Redis is not available"""

    def __init__(self):
        self.data = {}

    def ping(self) -> bool:
        """Mock ping - always returns True"""
        return True

    def get(self, key: str) -> Optional[str]:
        """Get value from mock store"""
        return self.data.get(key)

    def setex(self, key: str, time: int, value: str) -> bool:
        """Set value with expiration in mock store"""
        self.data[key] = value
        return True

    def delete(self, key: str) -> int:
        """Delete key from mock store"""
        if key in self.data:
            del self.data[key]
            return 1
        return 0

    def get_user_recommendations(self, user_id: int) -> Optional[List[int]]:
        """Get cached user recommendations"""
        key = f"user_recommendations:{user_id}"
        data = self.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None

    def set_user_recommendations(self, user_id: int, recommendations: List[int]) -> bool:
        """Cache user recommendations"""
        key = f"user_recommendations:{user_id}"
        try:
            data = json.dumps(recommendations)
            # Cache for 1 hour
            return self.setex(key, 3600, data)
        except (TypeError, ValueError):
            return False

    def delete_user_recommendations(self, user_id: int) -> bool:
        """Delete cached user recommendations"""
        key = f"user_recommendations:{user_id}"
        return self.delete(key) > 0


class RedisClient:
    """Redis client wrapper with fallback to mock client"""

    def __init__(self):
        if REDIS_AVAILABLE:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            try:
                self.client = redis.from_url(redis_url)
                # Test connection
                self.client.ping()
                self._use_mock = False
            except (redis.ConnectionError, redis.ResponseError):
                print("Warning: Redis connection failed, using mock client")
                self.client = MockRedisClient()
                self._use_mock = True
        else:
            print("Warning: Redis not available, using mock client")
            self.client = MockRedisClient()
            self._use_mock = True

    def ping(self) -> bool:
        """Test connection"""
        try:
            return self.client.ping()
        except Exception:
            return False

    def get(self, key: str) -> Optional[str]:
        """Get value"""
        try:
            return self.client.get(key)
        except Exception:
            return None

    def setex(self, key: str, time: int, value: str) -> bool:
        """Set value with expiration"""
        try:
            return self.client.setex(key, time, value)
        except Exception:
            return False

    def delete(self, key: str) -> int:
        """Delete key"""
        try:
            return self.client.delete(key)
        except Exception:
            return 0

    def get_user_recommendations(self, user_id: int) -> Optional[List[int]]:
        """Get cached user recommendations"""
        key = f"user_recommendations:{user_id}"
        data = self.get(key)
        if data:
            try:
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return json.loads(data)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
        return None

    def set_user_recommendations(self, user_id: int, recommendations: List[int]) -> bool:
        """Cache user recommendations"""
        key = f"user_recommendations:{user_id}"
        try:
            data = json.dumps(recommendations)
            # Cache for 1 hour
            return self.setex(key, 3600, data)
        except (TypeError, ValueError):
            return False

    def delete_user_recommendations(self, user_id: int) -> bool:
        """Delete cached user recommendations"""
        key = f"user_recommendations:{user_id}"
        return self.delete(key) > 0


# Global Redis client instance
redis_client = RedisClient()