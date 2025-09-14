# Konnect Recommendations System

This document describes the recommendations system implemented for the Konnect campus marketplace platform.

## Features

### 1. API Endpoint
- **Endpoint**: `GET /users/me/recommendations`
- **Authentication**: Required (Bearer token)
- **Response**: Returns cached recommendation data for the authenticated user
- **Status Codes**:
  - `200`: Success - returns recommendation data
  - `401`: Unauthorized - authentication required
  - `404`: No recommendations found - user should check back later

### 2. Background Task System
- **Technology**: Celery with Redis as broker
- **Schedule**: Runs every hour via Celery Beat
- **Tasks**:
  - `generate_recommendations_for_user`: Generate recommendations for a single user
  - `generate_recommendations_for_active_users`: Generate recommendations for all active users

### 3. Caching Layer
- **Technology**: Redis
- **Key Format**: `recommendations:user:{user_id}`
- **Expiration**: 1 hour (configurable via `REDIS_EXPIRE_TIME`)
- **Fallback**: Mock Redis client when Redis is unavailable

## API Response Format

```json
{
  "user_id": 1,
  "listing_ids": [1, 2, 3, 4, 5],
  "cached_at": "2024-01-01T10:30:00.000Z",
  "expires_at": "2024-01-01T11:30:00.000Z"
}
```

## Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_EXPIRE_TIME=3600

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## Running the System

### 1. Start the API Server
```bash
python main.py
```

### 2. Start Celery Worker (Production)
```bash
celery -A konnect.tasks worker --loglevel=info
```

### 3. Start Celery Beat Scheduler (Production)
```bash
celery -A konnect.tasks beat --loglevel=info
```

### 4. Development Demo
```bash
python demo_recommendations.py
```

## Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/test_recommendations.py -v
```

## Integration with Recommendation Agent

The system includes a mock recommendation agent that simulates the Google ADK integration. In production:

1. The agent analyzes user behavior and preferences
2. Generates personalized listing recommendations  
3. Returns a list of listing IDs sorted by relevance
4. Results are cached in Redis for fast API responses

## Architecture Flow

1. **Periodic Task**: Celery Beat triggers `generate_recommendations_for_active_users` every hour
2. **Agent Execution**: For each active user, the recommendation agent generates personalized suggestions
3. **Caching**: Results are stored in Redis with user-specific keys
4. **API Request**: When users call `/users/me/recommendations`, data is served from Redis cache
5. **Expiration**: Cache automatically expires after 1 hour, ensuring fresh recommendations

## Error Handling

- **Redis Unavailable**: Falls back to mock client for development
- **No Recommendations**: Returns 404 with helpful message
- **Authentication**: Proper 401 responses for unauthenticated requests
- **Task Failures**: Celery retry logic with exponential backoff

## Files Created/Modified

- `konnect/redis_client.py` - Redis client with fallback
- `konnect/tasks.py` - Celery tasks for background processing
- `konnect/routers/users.py` - Added recommendations endpoint
- `konnect/schemas.py` - Added RecommendationResponse schema
- `tests/test_recommendations.py` - Comprehensive test suite
- `demo_recommendations.py` - Demonstration script
- `celery_worker.py` - Worker runner script
- `requirements.txt` - Updated with Redis and Celery dependencies