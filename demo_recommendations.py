#!/usr/bin/env python3
"""
Demonstration script for the recommendations system

This script shows how the background task system works with the API endpoint.
It demonstrates:
1. Generating recommendations for users
2. Caching them in Redis
3. Retrieving them via the API endpoint (simulated)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from konnect.redis_client import redis_client
from konnect.tasks import generate_recommendations_now, mock_recommendation_agent
from konnect.schemas import RecommendationResponse
from datetime import datetime, timedelta


def demonstrate_recommendation_system():
    """Demonstrate the complete recommendation system"""
    
    print("=== Konnect Recommendations System Demo ===\n")
    
    # 1. Generate recommendations for several users
    print("1. Generating recommendations for users...")
    user_ids = [1, 2, 3, 4, 5]
    
    for user_id in user_ids:
        success = generate_recommendations_now(user_id)
        recommendations = redis_client.get_user_recommendations(user_id)
        print(f"   User {user_id}: {'✓' if success else '✗'} - {recommendations}")
    
    print()
    
    # 2. Simulate API endpoint behavior
    print("2. Simulating API endpoint responses...")
    
    for user_id in user_ids[:3]:  # Test first 3 users
        listing_ids = redis_client.get_user_recommendations(user_id)
        
        if listing_ids:
            # Simulate the API response
            cached_at = datetime.utcnow() - timedelta(minutes=30)
            expires_at = cached_at + timedelta(hours=1)
            
            response = RecommendationResponse(
                user_id=user_id,
                listing_ids=listing_ids,
                cached_at=cached_at,
                expires_at=expires_at
            )
            
            print(f"   User {user_id} recommendations: {response.listing_ids}")
            print(f"   Cached at: {response.cached_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Expires at: {response.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   User {user_id}: No recommendations found (404 error)")
        
        print()
    
    # 3. Test recommendation agent directly
    print("3. Testing recommendation agent directly...")
    
    for user_id in [10, 11, 12]:
        recommendations = mock_recommendation_agent(user_id)
        print(f"   User {user_id}: {recommendations}")
    
    print()
    
    # 4. Test cache operations
    print("4. Testing cache operations...")
    
    test_user_id = 99
    test_recommendations = [100, 101, 102, 103, 104]
    
    # Set
    success = redis_client.set_user_recommendations(test_user_id, test_recommendations)
    print(f"   Set recommendations for user {test_user_id}: {'✓' if success else '✗'}")
    
    # Get
    cached = redis_client.get_user_recommendations(test_user_id)
    print(f"   Retrieved recommendations: {cached}")
    
    # Delete
    success = redis_client.delete_user_recommendations(test_user_id)
    print(f"   Deleted recommendations: {'✓' if success else '✗'}")
    
    # Verify deleted
    cached = redis_client.get_user_recommendations(test_user_id)
    print(f"   Verify deletion (should be None): {cached}")
    
    print()
    
    # 5. Demonstrate the periodic task behavior
    print("5. Simulating periodic background task...")
    print("   In production, this would run every hour via Celery Beat")
    print("   Task: generate_recommendations_for_active_users")
    
    active_users = [1, 2, 3, 4, 5]
    success_count = 0
    
    for user_id in active_users:
        try:
            success = generate_recommendations_now(user_id)
            if success:
                success_count += 1
        except Exception as e:
            print(f"   Error for user {user_id}: {e}")
    
    print(f"   Background task result: {success_count}/{len(active_users)} users updated")
    
    print("\n=== Demo Complete ===")
    print("\nTo test the API endpoint:")
    print("1. Start the server: python main.py")
    print("2. Make authenticated request to: GET /users/me/recommendations")
    print("3. The endpoint will return cached recommendations from Redis")


if __name__ == "__main__":
    demonstrate_recommendation_system()