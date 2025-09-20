"""
Agents module for Konnect

This module contains AI agents powered by Google ADK for various tasks
including recommendations, semantic search, price suggestion, description generation,
and fraud detection.
"""

from .recommendation import RecommendationAgent, create_recommendation_agent, root_agent
from .semantic_search import (
    SemanticSearchAgent,
    create_semantic_search_agent,
    semantic_search_root_agent,
)
from .price_suggestion import (
    PriceSuggestionAgent,
    create_price_suggestion_agent,
    price_suggestion_root_agent,
)
from .description_generation import (
    DescriptionGenerationAgent,
    create_description_generation_agent,
    description_generation_root_agent,
)
from .fraud_detection import (
    FraudDetectionAgent,
    create_fraud_detection_agent,
    fraud_detection_root_agent,
)

__all__ = [
    # Recommendation Agent
    "RecommendationAgent",
    "create_recommendation_agent",
    "root_agent",
    # Semantic Search Agent
    "SemanticSearchAgent",
    "create_semantic_search_agent",
    "semantic_search_root_agent",
    # Price Suggestion Agent
    "PriceSuggestionAgent",
    "create_price_suggestion_agent",
    "price_suggestion_root_agent",
    # Description Generation Agent
    "DescriptionGenerationAgent",
    "create_description_generation_agent",
    "description_generation_root_agent",
    # Fraud Detection Agent
    "FraudDetectionAgent",
    "create_fraud_detection_agent",
    "fraud_detection_root_agent",
]
