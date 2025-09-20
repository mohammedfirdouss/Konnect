# Konnect AI Agents

This directory contains AI agents powered by Google ADK (Agent Development Kit) for the Konnect campus marketplace platform.

## Agent Structure

Each agent follows Google ADK best practices and includes:

1. **YAML Configuration File** - Agent configuration following ADK standards
2. **Python Implementation** - Agent class with ADK integration
3. **Tool Functions** - Database interaction functions for the agent
4. **Factory Functions** - Easy agent creation and initialization
5. **ADK CLI Compatibility** - Root agents for CLI testing

## Available Agents

### 1. Recommendation Agent (`recommendation.py`)
- **Purpose**: Provides personalized recommendations for users
- **YAML Config**: `root_agent.yaml` (legacy)
- **Root Agent**: `root_agent`
- **Tools**: `get_popular_items`, `search_items_by_category`, `get_price_range_items`, `get_user_activity`

### 2. Semantic Search Agent (`semantic_search.py`)
- **Purpose**: Natural language search with AI interpretation
- **YAML Config**: `semantic_search_agent.yaml`
- **Root Agent**: `semantic_search_root_agent`
- **Tools**: `search_listings_by_keywords`, `get_listings_by_category`, `get_listings_by_price_range`

### 3. Price Suggestion Agent (`price_suggestion.py`)
- **Purpose**: AI-powered price analysis and suggestions for sellers
- **YAML Config**: `price_suggestion_agent.yaml`
- **Root Agent**: `price_suggestion_root_agent`
- **Tools**: `get_similar_listings`, `get_market_price_stats`, `analyze_price_trends`

### 4. Description Generation Agent (`description_generation.py`)
- **Purpose**: AI-generated compelling product descriptions
- **YAML Config**: `description_generation_agent.yaml`
- **Root Agent**: `description_generation_root_agent`
- **Tools**: `get_category_examples`, `get_popular_keywords`, `analyze_description_quality`

### 5. Fraud Detection Agent (`fraud_detection.py`)
- **Purpose**: AI-powered fraud detection and risk assessment
- **YAML Config**: `fraud_detection_agent.yaml`
- **Root Agent**: `fraud_detection_root_agent`
- **Tools**: `analyze_user_activity`, `analyze_listing_patterns`, `get_recent_fraud_indicators`

## Google ADK Compatibility

All agents are designed to be fully compatible with Google ADK:

### Features Implemented:
- ✅ **Agent Configuration**: YAML files following ADK standards
- ✅ **Tool Integration**: Database functions as ADK tools
- ✅ **Session Management**: InMemorySessionService for conversation state
- ✅ **Safety Settings**: Proper harm category configurations
- ✅ **Content Generation**: Structured response handling
- ✅ **Error Handling**: Graceful fallback when ADK unavailable
- ✅ **CLI Compatibility**: Root agents for ADK CLI testing

### ADK Best Practices Followed:
1. **Agent Naming**: Consistent naming convention (`konnect_*_agent`)
2. **Tool Definitions**: Clear tool signatures and documentation
3. **Instruction Design**: Comprehensive agent instructions
4. **Safety Configuration**: Appropriate safety thresholds
5. **Model Configuration**: Optimized temperature and token settings
6. **Error Handling**: Robust error handling and fallback mechanisms

## Usage Examples

### Creating Agents Programmatically:
```python
from konnect.agents import (
    create_semantic_search_agent,
    create_price_suggestion_agent,
    create_description_generation_agent,
    create_fraud_detection_agent
)

# Create agents
search_agent = create_semantic_search_agent()
price_agent = create_price_suggestion_agent()
desc_agent = create_description_generation_agent()
fraud_agent = create_fraud_detection_agent()
```

### Using Root Agents for CLI Testing:
```python
from konnect.agents import (
    semantic_search_root_agent,
    price_suggestion_root_agent,
    description_generation_root_agent,
    fraud_detection_root_agent
)

# These can be used with ADK CLI for testing
```

### YAML Configuration:
Each agent has a corresponding YAML file that can be used with ADK CLI:
```bash
# Example ADK CLI usage
adk run semantic_search_agent.yaml
adk run price_suggestion_agent.yaml
adk run description_generation_agent.yaml
adk run fraud_detection_agent.yaml
```

## API Integration

All agents are integrated with the FastAPI application through the AI router (`/ai/` endpoints):

- `POST /ai/search` - Semantic search
- `POST /ai/suggest-price` - Price suggestions
- `POST /ai/generate-description` - Description generation
- `GET /admin/ai/fraud-reports` - Fraud detection (admin only)

## Development Notes

### Adding New Agents:
1. Create YAML configuration file
2. Implement Python agent class with ADK integration
3. Define tool functions for database interaction
4. Add factory function and root agent
5. Update `__init__.py` exports
6. Add API endpoints in router

### Testing:
- Use root agents for CLI testing
- Mock mode available when ADK unavailable
- Comprehensive error handling
- Graceful degradation

### Performance:
- Session management for conversation state
- Efficient database queries
- Caching considerations
- Rate limiting for AI services

## Dependencies

- Google ADK (Agent Development Kit)
- Google GenAI
- SQLAlchemy (database access)
- FastAPI (API integration)
- Pydantic (data validation)

## Fallback Mode

When Google ADK is not available, all agents run in mock mode with:
- Basic functionality preserved
- Clear error messages
- Graceful degradation
- No service disruption