"""Background tasks for recommendation generation using Celery"""

import os
from typing import List
from celery import Celery
from celery.schedules import crontab

from .redis_client import redis_client

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Create Celery app
celery_app = Celery(
    "konnect_recommendations",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["konnect.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Periodic task configuration
    beat_schedule={
        "generate-recommendations": {
            "task": "konnect.tasks.generate_recommendations_for_active_users",
            "schedule": crontab(minute=0),  # Run every hour
        },
    },
)


def mock_recommendation_agent(user_id: int) -> List[int]:
    """Mock recommendation agent that returns sample listing IDs
    
    This replaces the Google ADK agent until it's properly configured.
    In production, this would call the actual RecommendationAgent.
    
    Args:
        user_id: The user ID to generate recommendations for
        
    Returns:
        List of recommended listing IDs
    """
    # Mock data - in production this would use the actual recommendation agent
    # The agent would analyze user behavior, preferences, and generate personalized recommendations
    base_recommendations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Vary recommendations slightly based on user_id to make them feel personalized
    offset = (user_id % 5)
    personalized_recommendations = [
        (listing_id + offset) % 20 + 1 
        for listing_id in base_recommendations
    ]
    
    # Return top 5 recommendations
    return personalized_recommendations[:5]


@celery_app.task(bind=True)
def generate_recommendations_for_user(self, user_id: int) -> bool:
    """Generate and cache recommendations for a single user
    
    Args:
        user_id: The user ID to generate recommendations for
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate recommendations using the agent
        listing_ids = mock_recommendation_agent(user_id)
        
        # Cache the recommendations in Redis
        success = redis_client.set_user_recommendations(user_id, listing_ids)
        
        if success:
            self.retry_count = 0  # Reset retry count on success
            return True
        else:
            raise Exception("Failed to cache recommendations")
            
    except Exception as exc:
        # Retry logic
        if self.request.retries < 3:
            self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)
        return False


@celery_app.task(bind=True)
def generate_recommendations_for_active_users(self):
    """Generate recommendations for all active users
    
    This task is scheduled to run periodically and generates fresh recommendations
    for all active users in the system.
    """
    try:
        # Mock active user IDs - in production this would query the database
        # for users who have been active recently
        active_user_ids = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30]
        
        success_count = 0
        failure_count = 0
        
        for user_id in active_user_ids:
            try:
                # Generate recommendations for each user
                result = generate_recommendations_for_user.delay(user_id)
                if result:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception:
                failure_count += 1
        
        print(f"Recommendation generation completed: {success_count} successful, {failure_count} failed")
        return {"success": success_count, "failures": failure_count}
        
    except Exception as exc:
        print(f"Failed to generate recommendations for active users: {exc}")
        return {"success": 0, "failures": 0}


# For testing purposes - function to manually trigger recommendation generation
def generate_recommendations_now(user_id: int) -> bool:
    """Manually generate recommendations for a user (for testing)
    
    Args:
        user_id: The user ID to generate recommendations for
        
    Returns:
        True if successful, False otherwise
    """
    try:
        listing_ids = mock_recommendation_agent(user_id)
        return redis_client.set_user_recommendations(user_id, listing_ids)
    except Exception:
        return False