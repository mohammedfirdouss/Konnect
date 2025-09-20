# Konnect - Campus Tools with SolanaPay

A comprehensive campus marketplace platform built with FastAPI, featuring AI-powered recommendations using Google ADK and Solana blockchain integration for payments.

## 🏗️ Project Architecture

### Backend Structure
```
konnect/
├── main.py                 # FastAPI application entry point
├── auth.py                 # JWT authentication utilities
├── database.py             # SQLAlchemy database configuration
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic schemas for API validation
├── crud.py                 # Database CRUD operations
├── dependencies.py         # FastAPI dependencies
├── redis_client.py         # Redis client for caching
├── tasks.py                # Celery background tasks
├── routers/                # API route modules
│   ├── auth.py            # Authentication endpoints
│   ├── users.py           # User management endpoints
│   └── listings.py        # Marketplace listing endpoints
└── agents/                 # AI recommendation agents
    └── recommendation.py  # Google ADK-powered recommendation agent
```

### Key Features
- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **JWT Authentication**: Secure user authentication and authorization
- **SQLAlchemy ORM**: Database abstraction with SQLite/PostgreSQL support
- **Redis Caching**: High-performance caching for recommendations
- **Google ADK Integration**: AI-powered recommendation engine
- **Solana Integration**: Blockchain payments via SolanaPay
- **OpenTelemetry**: Comprehensive monitoring and metrics
- **Celery**: Background task processing
- **Docker Support**: Containerized deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Poetry (recommended) or pip
- Docker (optional)
- Google Cloud credentials (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Konnect
   ```

2. **Install dependencies with Poetry (recommended)**
   ```bash
   # Install Poetry if you haven't already
   curl -sSL https://install.python-poetry.org | python3 -

   # Install project dependencies
   poetry install

   # Activate the virtual environment
   poetry shell
   ```

   **OR install with pip**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create a .env file
   cp .env.example .env

   # Edit .env with your configuration
   nano .env
   ```

   **Required environment variables:**
   ```env
   # Database
   DATABASE_URL=sqlite:///./konnect.db

   # Authentication
   SECRET_KEY=your-secret-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Google ADK (for AI recommendations)
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

   # Redis (optional, for caching)
   REDIS_URL=redis://localhost:6379
   ```

4. **Initialize the database**
   ```bash
   # The database tables will be created automatically on first run
   python main.py
   ```

5. **Run the development server**
   ```bash
   # Using Poetry
   poetry run uvicorn konnect.main:app --reload --host 0.0.0.0 --port 8000

   # OR using pip
   uvicorn konnect.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   - **API**: http://localhost:8000
   - **Interactive API Docs**: http://localhost:8000/docs
   - **ReDoc Documentation**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health
   - **Metrics**: http://localhost:8000/metrics

## 🤖 Google ADK Integration

### What is Google ADK?
Google ADK (Agent Development Kit) is Google's framework for building AI agents with access to Google's Generative AI models. In this project, it powers the recommendation system.

### Setup Google ADK

1. **Install Google ADK**
   ```bash
   # Already included in pyproject.toml
   poetry install
   ```

2. **Set up Google Cloud credentials**
   ```bash
   # Option 1: Service Account Key (recommended for development)
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

   # Option 2: Application Default Credentials (recommended for production)
   gcloud auth application-default login
   ```

3. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the following APIs:
     - Vertex AI API
     - Generative AI API
   - Create a service account and download the JSON key

### How Google ADK Works in Konnect

The recommendation agent (`konnect/agents/recommendation.py`) uses Google ADK to:

1. **Analyze user behavior**: Tracks purchase history, browsing patterns, and preferences
2. **Generate personalized recommendations**: Uses AI to suggest relevant items
3. **Provide intelligent search**: Understands natural language queries
4. **Budget-aware suggestions**: Considers price ranges and student budgets

**Key Components:**
- `RecommendationAgent`: Main AI agent class
- `get_user_activity()`: Retrieves user behavior data
- `get_popular_items()`: Gets trending marketplace items
- `search_items_by_category()`: Category-based filtering
- `get_price_range_items()`: Budget-based filtering

### Testing Google ADK Integration

#### Using ADK in Terminal Mode
For quick, stateless functional checks and development testing:

```bash
# Install ADK CLI (if not already available)
pip install google-adk

# Run agent in terminal mode (interactive testing)
adk run konnect/agents/

# This will start an interactive session where you can chat with the agent
# Type your questions and press Enter, type 'exit' to quit
```

#### Using ADK Web Interface
For interactive testing and debugging with full UI:

```bash
# Start ADK web server for interactive testing
adk web konnect/

# Note: If port 8000 is in use by the main Konnect app, you may need to:
# 1. Stop the main FastAPI server first, or
# 2. Use a different port: adk web konnect/ --port 8001

# This will:
# 1. Start a local web server (typically on port 8000)
# 2. Open your browser to the ADK web interface
# 3. Allow you to select agents from a dropdown menu
# 4. Provide an interactive chat interface for testing
```

#### Running Automated Tests

```bash
# Run agent-specific tests
pytest tests/test_agents.py -v

# Test with mock data (no Google credentials needed)
pytest tests/test_agents.py::TestRecommendationAgentTools -v

# Run all tests with coverage
pytest --cov=konnect --cov-report=html --cov-report=term-missing
```

#### Testing Strategies

1. **Unit Tests** (`test_agents.py`): Test individual agent tools and functions
2. **Integration Tests**: Test agent interactions with the full Konnect system
3. **Terminal Testing**: Interactive chat with agent using `adk run` (✅ Working)
4. **Web Testing**: Browser-based interface for testing using `adk web` (✅ Working)
5. **Mock Testing**: Test agent logic without requiring Google API credentials

### Current Status
- ✅ **Terminal Mode**: `adk run konnect/agents/` successfully loads and runs the agent
- ✅ **Web Mode**: `adk web konnect/` starts the web server (use different port if 8000 is occupied)
- ✅ **Agent Structure**: Properly configured with tools and instructions
- ⚠️ **Google Credentials**: Required for AI responses - currently missing API key/credentials

### Setting Up Google Credentials for Full AI Functionality

To enable actual AI responses (not just mock responses), you need Google credentials:

1. **Get Google AI API Key** (recommended for development):
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create an API key
   - Add to `.env`: `GOOGLE_API_KEY=your_api_key_here`

2. **OR use Google Cloud credentials**:
   - Uncomment the line in `.env`: `GOOGLE_APPLICATION_CREDENTIALS=/workspace/Konnect/google-credentials.json`
   - Follow the Google Cloud setup instructions in the "Google ADK Integration" section above

3. **Test with credentials**:
   ```bash
   # With API key
   adk run konnect/agents/

   # With Cloud credentials
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   adk run konnect/agents/
   ```

**Note**: Without credentials, the agent will load but fail when generating responses. The mock mode in our Python agent provides fallback responses for testing the agent structure.

### Google ADK Best Practices

#### Agent Development Guidelines
1. **Code-First Approach**: Define everything in Python code for versioning, testing, and IDE support
2. **Model Agnostic**: Keep agent logic separate from deployment environment
3. **Clear Naming**: Use descriptive names for agents, tools, and functions
4. **Comprehensive Instructions**: Provide detailed instructions for agent behavior and capabilities
5. **Tool Integration**: Design tools to be reusable and well-documented

#### Project Structure
```
konnect/agents/
├── recommendation.py          # Main recommendation agent
├── __init__.py               # Package initialization
└── [future_agents]/          # Additional agents as needed
```

#### Safety and Security
- Implement appropriate safety settings for content generation
- Use environment variables for API keys and sensitive configuration
- Validate all tool inputs and outputs
- Set appropriate temperature and token limits for consistent responses

#### Testing Best Practices
- **Mock External Dependencies**: Test agent logic without API calls
- **Use Multiple Testing Methods**: Combine unit tests, terminal testing, and web testing
- **Test Error Scenarios**: Ensure agents handle failures gracefully
- **Validate Tool Functions**: Test each tool independently before integration
- **Performance Testing**: Monitor response times and resource usage

### Recommended Additional Agents

Based on the ADK framework and Konnect's campus marketplace focus, consider implementing these additional agents:

#### 1. **Market Analysis Agent**
- **Purpose**: Analyze market trends, pricing patterns, and demand
- **Tools**: Price analysis, trend detection, competitor monitoring
- **Benefits**: Help sellers set optimal prices, identify trending categories

#### 2. **Fraud Detection Agent**
- **Purpose**: Detect suspicious listings and transactions
- **Tools**: Pattern recognition, anomaly detection, user behavior analysis
- **Benefits**: Maintain platform trust and safety

#### 3. **Negotiation Agent**
- **Purpose**: Assist with price negotiations between buyers and sellers
- **Tools**: Market value assessment, negotiation strategy, communication facilitation
- **Benefits**: Improve transaction success rates

#### 4. **Quality Assurance Agent**
- **Purpose**: Review listings for completeness and quality
- **Tools**: Content analysis, image validation, description enhancement
- **Benefits**: Improve listing quality and user experience

#### 5. **Community Agent**
- **Purpose**: Foster community engagement and campus connections
- **Tools**: Event suggestions, study group formation, local recommendations
- **Benefits**: Build campus community and increase user engagement

#### Implementation Strategy
1. Start with one additional agent based on user feedback
2. Use the existing recommendation agent as a template
3. Follow ADK best practices for consistency
4. Test thoroughly using both terminal and web modes
5. Integrate with existing Konnect infrastructure

## 🧪 Testing the Backend

### Running Tests

1. **Run all tests**
   ```bash
   # Using Poetry
   poetry run pytest

   # OR using pip
   pytest
   ```

2. **Run specific test categories**
   ```bash
   # API endpoint tests
   pytest tests/test_api.py -v

   # Database tests
   pytest tests/test_database.py -v

   # Model tests
   pytest tests/test_models.py -v

   # Agent/AI tests
   pytest tests/test_agents.py -v

   # Solana integration tests
   pytest tests/test_solana.py -v
   ```

3. **Run tests with coverage**
   ```bash
   pytest --cov=konnect --cov-report=html --cov-report=term-missing
   ```

### Test Categories

#### 1. **API Tests** (`test_api.py`)
- Tests all HTTP endpoints
- Validates request/response schemas
- Tests authentication flows
- Verifies error handling

#### 2. **Database Tests** (`test_database.py`)
- Tests database connections
- Validates CRUD operations
- Tests data integrity
- Verifies relationships

#### 3. **Model Tests** (`test_models.py`)
- Tests SQLAlchemy models
- Validates data validation
- Tests model relationships
- Verifies constraints

#### 4. **Agent Tests** (`test_agents.py`)
- Tests recommendation logic
- Validates AI agent responses
- Tests tool functions
- Mocks Google ADK when needed

#### 5. **Authentication Tests** (`test_auth.py`)
- Tests JWT token generation
- Validates password hashing
- Tests authentication flows
- Verifies authorization

### Manual API Testing

1. **Using the Interactive Docs**
   - Visit http://localhost:8000/docs
   - Click "Authorize" and enter a JWT token
   - Test endpoints directly in the browser

2. **Using curl**
   ```bash
   # Health check
   curl http://localhost:8000/health

   # Register a user
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "email": "test@example.com", "password": "testpass", "full_name": "Test User"}'

   # Login
   curl -X POST "http://localhost:8000/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=testuser&password=testpass"

   # Get listings (requires authentication)
   curl -X GET "http://localhost:8000/listings/" \
        -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Using Postman/Insomnia**
   - Import the OpenAPI spec from http://localhost:8000/openapi.json
   - Set up authentication headers
   - Test all endpoints systematically

## 🐳 Docker Deployment

### Using Docker Compose

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f konnect
   ```

4. **Stop services**
   ```bash
   docker-compose down
   ```

### Manual Docker Build

```bash
# Build the image
docker build -t konnect .

# Run the container
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./konnect.db \
  -e SECRET_KEY=your-secret-key \
  konnect
```

## 📊 Monitoring and Observability

### Metrics Endpoint
- **Prometheus Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health

### Logging
- **Structured JSON Logging**: All logs are in JSON format
- **Log Levels**: INFO, WARNING, ERROR, DEBUG
- **Request Tracking**: Each request has a unique ID

### OpenTelemetry Integration
- **Tracing**: Request flow tracking
- **Metrics**: Performance and usage metrics
- **Export**: Prometheus-compatible metrics

## 🔧 Development

### Code Quality Tools

1. **Ruff (Linting)**
   ```bash
   poetry run ruff check .
   poetry run ruff format .
   ```

2. **Type Checking**
   ```bash
   poetry run mypy konnect/
   ```

3. **Pre-commit Hooks**
   ```bash
   # Install pre-commit
   pip install pre-commit

   # Install hooks
   pre-commit install
   ```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Features

1. **Create new models** in `konnect/models.py`
2. **Add schemas** in `konnect/schemas.py`
3. **Implement CRUD** in `konnect/crud.py`
4. **Create router** in `konnect/routers/`
5. **Add tests** in `tests/`
6. **Update documentation**

## 🚨 Troubleshooting

### Common Issues

1. **Google ADK Import Error**
   ```bash
   # Ensure Google ADK is installed
   poetry install

   # Check Google credentials
   echo $GOOGLE_APPLICATION_CREDENTIALS
   ```

2. **Database Connection Issues**
   ```bash
   # Check database URL
   echo $DATABASE_URL

   # Verify database file permissions
   ls -la konnect.db
   ```

3. **Authentication Issues**
   ```bash
   # Check secret key
   echo $SECRET_KEY

   # Verify JWT token format
   # Token should be: Bearer <jwt_token>
   ```

4. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000

   # Kill the process
   kill -9 <PID>
   ```

### Debug Mode

```bash
# Run with debug logging
PYTHONPATH=/workspace/Konnect python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from konnect.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000, log_level='debug')
"
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get JWT token

### User Endpoints
- `GET /users/me` - Get current user info
- `GET /users/me/recommendations` - Get personalized recommendations

### Listing Endpoints
- `GET /listings/` - Get all listings (with pagination/filtering)
- `POST /listings/` - Create new listing (authenticated)
- `GET /listings/{id}` - Get specific listing
- `PUT /listings/{id}` - Update listing (owner only)
- `DELETE /listings/{id}` - Delete listing (owner only)

### Marketplaces Endpoints
- `GET /marketplaces/` - Get all available marketplaces
- `GET /marketplaces/{id}` - Get marketplace details
- `POST /marketplaces/request` - Request creation of new marketplace
- `GET /marketplaces/{id}/products` - Get products in marketplace

### Orders & Escrow Endpoints
- `POST /orders/` - Create order with Solana escrow (buyer only)
- `GET /orders/{id}` - Get order details (buyer/seller only)
- `POST /orders/{id}/confirm-delivery` - Confirm delivery & release funds (buyer only)
- `POST /orders/{id}/dispute` - Raise dispute on order (buyer only)

### Admin Endpoints
- `GET /admin/stats` - Get admin dashboard statistics
- `GET /admin/marketplace/sellers/pending` - Get sellers awaiting verification
- `POST /admin/marketplace/sellers/{id}/verify` - Verify seller & mint NFT
- `DELETE /admin/marketplace/products/{id}` - Remove fraudulent listing
- `GET /admin/marketplace/requests` - Get marketplace creation requests
- `POST /admin/marketplace/requests/{id}/approve` - Approve marketplace request
- `POST /admin/marketplace/requests/{id}/reject` - Reject marketplace request

### AI & Recommendations Endpoints
- `GET /ai/recommendations` - Get AI-powered personalized recommendations
- `GET /ai/seller-insights` - Get seller analytics & insights
- `GET /ai/market-analysis` - Get market analysis (placeholder)

### Products & Search Endpoints
- `GET /products/search` - Advanced product search with filters
- `GET /products/categories` - Get all product categories
- `GET /products/trending` - Get trending products
- `GET /products/recommendations/{id}` - Get related products

### System Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the API documentation at http://localhost:8000/docs
3. Check the test files for usage examples
4. Open an issue on GitHub

---

**Happy coding! 🚀**
