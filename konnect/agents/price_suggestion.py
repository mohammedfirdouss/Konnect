"""
Price Suggestion Agent for Konnect Campus Marketplace

This module implements a price suggestion agent that analyzes market data
to suggest optimal pricing for sellers.
"""

import os
import sys
from typing import Any, Dict, List, Optional

# Add the project root to the Python path for database access
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Local imports
from konnect import crud  # noqa: E402
from konnect.database import SessionLocal  # noqa: E402

# Conditional Google ADK imports
try:
    from google.adk import Agent, Runner  # noqa: E402
    from google.adk.sessions.in_memory_session_service import (  # noqa: E402
        InMemorySessionService,
    )
    from google.genai import types  # noqa: E402

    ADK_AVAILABLE = True
except ImportError:
    # Create mock classes when ADK is not available
    ADK_AVAILABLE = False  # noqa: E402

    class Agent:  # noqa: E402
        def __init__(self, *args, **kwargs):
            pass

    class Runner:  # noqa: E402
        def __init__(self, *args, **kwargs):
            pass

        def run(self, *args, **kwargs):
            return []

    class InMemorySessionService:  # noqa: E402
        def create_session(self, *args, **kwargs):
            class MockSession:
                id = "mock_session"

            return MockSession()

    class types:  # noqa: E402
        class GenerateContentConfig:
            def __init__(self, **kwargs):
                pass

        class SafetySetting:
            def __init__(self, **kwargs):
                pass

        class Content:
            def __init__(self, **kwargs):
                pass

        class Part:
            @staticmethod
            def from_text(**kwargs):
                return None

        class HarmCategory:
            HARM_CATEGORY_HARASSMENT = "harassment"
            HARM_CATEGORY_HATE_SPEECH = "hate_speech"

        class HarmBlockThreshold:
            BLOCK_MEDIUM_AND_ABOVE = "medium_and_above"


def get_similar_listings(
    title: str, category: Optional[str] = None, brand: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get similar listings for price comparison.

    Args:
        title: Listing title to find similar items for
        category: Optional category filter
        brand: Optional brand filter

    Returns:
        List of similar listings with prices
    """
    db = SessionLocal()
    try:
        # Get listings in the same category if provided
        if category:
            listings = crud.get_listings(db, category=category, limit=50)
        else:
            listings = crud.get_listings(db, limit=100)

        # Simple similarity matching based on keywords
        title_keywords = set(title.lower().split())
        similar_listings = []

        for listing in listings:
            listing_keywords = set(listing.title.lower().split())

            # Calculate keyword overlap
            overlap = len(title_keywords.intersection(listing_keywords))
            similarity_score = overlap / len(title_keywords) if title_keywords else 0

            # Include if similarity is above threshold or brand matches
            if similarity_score > 0.3 or (
                brand and brand.lower() in listing.title.lower()
            ):
                seller = crud.get_user(db, listing.user_id)
                marketplace = crud.get_marketplace(db, listing.marketplace_id)

                similar_listings.append(
                    {
                        "listing_id": listing.id,
                        "title": listing.title,
                        "price": listing.price,
                        "category": listing.category,
                        "seller_username": seller.username if seller else "Unknown",
                        "marketplace_name": marketplace.name
                        if marketplace
                        else "Unknown",
                        "similarity_score": similarity_score,
                        "created_at": listing.created_at.isoformat(),
                    }
                )

        # Sort by similarity score and return top matches
        similar_listings.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_listings[:10]

    finally:
        db.close()


def get_market_price_stats(category: Optional[str] = None) -> Dict[str, Any]:
    """Get market price statistics for a category.

    Args:
        category: Optional category to analyze

    Returns:
        Dictionary with price statistics
    """
    db = SessionLocal()
    try:
        if category:
            listings = crud.get_listings(db, category=category, limit=200)
        else:
            listings = crud.get_listings(db, limit=500)

        if not listings:
            return {
                "average_price": 0.0,
                "median_price": 0.0,
                "min_price": 0.0,
                "max_price": 0.0,
                "price_range": "No data available",
                "total_listings": 0,
            }

        prices = [listing.price for listing in listings]
        prices.sort()

        avg_price = sum(prices) / len(prices)
        median_price = prices[len(prices) // 2]
        min_price = min(prices)
        max_price = max(prices)

        # Determine price range category
        if avg_price < 25:
            price_range = "Budget-friendly"
        elif avg_price < 100:
            price_range = "Mid-range"
        elif avg_price < 500:
            price_range = "Premium"
        else:
            price_range = "High-end"

        return {
            "average_price": round(avg_price, 2),
            "median_price": round(median_price, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "price_range": price_range,
            "total_listings": len(listings),
        }

    finally:
        db.close()


def analyze_price_trends(category: Optional[str] = None) -> Dict[str, Any]:
    """Analyze price trends for a category.

    Args:
        category: Optional category to analyze

    Returns:
        Dictionary with trend analysis
    """
    db = SessionLocal()
    try:
        if category:
            listings = crud.get_listings(db, category=category, limit=200)
        else:
            listings = crud.get_listings(db, limit=500)

        if not listings:
            return {
                "trend": "stable",
                "trend_description": "No data available",
                "competition_level": "unknown",
            }

        # Simple trend analysis based on listing age and price
        recent_listings = [listing for listing in listings if listing.created_at]
        if recent_listings:
            recent_prices = [
                listing.price for listing in recent_listings[-10:]
            ]  # Last 10 listings
            older_prices = (
                [listing.price for listing in recent_listings[:-10]]
                if len(recent_listings) > 10
                else []
            )

            if older_prices:
                recent_avg = sum(recent_prices) / len(recent_prices)
                older_avg = sum(older_prices) / len(older_prices)

                if recent_avg > older_avg * 1.1:
                    trend = "rising"
                    trend_description = "Prices are trending upward"
                elif recent_avg < older_avg * 0.9:
                    trend = "falling"
                    trend_description = "Prices are trending downward"
                else:
                    trend = "stable"
                    trend_description = "Prices are relatively stable"
            else:
                trend = "stable"
                trend_description = "Insufficient data for trend analysis"
        else:
            trend = "stable"
            trend_description = "No recent listings for trend analysis"

        # Determine competition level
        total_listings = len(listings)
        if total_listings > 50:
            competition_level = "high"
        elif total_listings > 20:
            competition_level = "medium"
        else:
            competition_level = "low"

        return {
            "trend": trend,
            "trend_description": trend_description,
            "competition_level": competition_level,
        }

    finally:
        db.close()


class PriceSuggestionAgent:
    """AI-powered price suggestion agent for the Konnect campus marketplace."""

    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """Initialize the price suggestion agent."""
        if not ADK_AVAILABLE:
            print("Warning: Google ADK not available. Agent will run in mock mode.")
            self.agent = None
            self.session_service = None
            self.runner = None
            self.session_id = None
            self._initialized = False
            return

        self.model = model
        try:
            # Create the agent
            self.agent = Agent(
                model=self.model,
                name="konnect_price_suggestion_agent",
                instruction="""You are a price suggestion agent for Konnect, a campus marketplace platform.
                Your role is to analyze market data and suggest optimal pricing for sellers.

                Guidelines:
                - Analyze similar listings and market trends
                - Consider condition, brand, and category factors
                - Provide competitive pricing recommendations
                - Explain your reasoning clearly
                - Consider student budgets and campus market dynamics
                - Suggest price ranges with confidence scores
                - Factor in seasonal trends and demand patterns

                Available Tools:
                1. get_similar_listings(title, category, brand) - Find similar items for comparison
                2. get_market_price_stats(category) - Get market price statistics
                3. analyze_price_trends(category) - Analyze price trends and competition

                When suggesting prices:
                1. Analyze similar listings and their prices
                2. Consider market statistics and trends
                3. Factor in item condition, brand, and uniqueness
                4. Provide a price range with reasoning
                5. Include confidence score and market analysis
                6. Suggest pricing strategies (e.g., competitive, premium, quick-sale)""",
                tools=[
                    get_similar_listings,
                    get_market_price_stats,
                    analyze_price_trends,
                ],
                generate_content_config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        ),
                    ],
                    temperature=0.4,  # Balanced creativity for price analysis
                    top_p=0.8,
                    max_output_tokens=1200,
                ),
            )

            # Create session service and runner
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="konnect_price_suggestion",
                agent=self.agent,
                session_service=self.session_service,
            )
            self.session_id = None
            self._initialized = True

        except Exception as e:
            print(f"Warning: Failed to initialize ADK components: {e}")
            self.agent = None
            self.session_service = None
            self.runner = None
            self._initialized = False

    def suggest_price(
        self,
        title: str,
        category: Optional[str] = None,
        condition: Optional[str] = None,
        brand: Optional[str] = None,
        additional_details: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest optimal pricing for a listing.

        Args:
            title: Listing title
            category: Item category
            condition: Item condition
            brand: Item brand
            additional_details: Additional details about the item

        Returns:
            Dictionary containing price suggestions and analysis
        """
        if not ADK_AVAILABLE:
            # Mock response when ADK is not available
            return {
                "suggested_price_range": {
                    "min": 25.0,
                    "max": 75.0,
                    "recommended": 50.0,
                },
                "market_analysis": {
                    "average_price": 50.0,
                    "price_trend": "stable",
                    "competition_level": "medium",
                },
                "reasoning": "Mock price suggestion: Google ADK not available. In a real environment, this would provide detailed price analysis.",
                "similar_listings": [],
                "confidence_score": 0.5,
            }

        if not self.runner:
            return {
                "suggested_price_range": {"min": 0.0, "max": 0.0, "recommended": 0.0},
                "market_analysis": {
                    "average_price": 0.0,
                    "price_trend": "unknown",
                    "competition_level": "unknown",
                },
                "reasoning": "Sorry, I couldn't initialize the price suggestion system.",
                "similar_listings": [],
                "confidence_score": 0.0,
            }

        try:
            # Create a user message content
            query_parts = [f"Suggest pricing for: {title}"]
            if category:
                query_parts.append(f"Category: {category}")
            if condition:
                query_parts.append(f"Condition: {condition}")
            if brand:
                query_parts.append(f"Brand: {brand}")
            if additional_details:
                query_parts.append(f"Additional details: {additional_details}")

            user_message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=". ".join(query_parts))],
            )

            # Create a session if we don't have one
            if not self.session_id and self.session_service:
                import asyncio

                try:
                    session = asyncio.run(
                        self.session_service.create_session(
                            app_name="konnect_price_suggestion",
                            user_id="price_user",
                        )
                    )
                    self.session_id = session.id
                except RuntimeError:
                    # If we're already in an event loop, create session synchronously
                    import nest_asyncio

                    nest_asyncio.apply()
                    session = asyncio.run(
                        self.session_service.create_session(
                            app_name="konnect_price_suggestion",
                            user_id="price_user",
                        )
                    )
                    self.session_id = session.id

            # Run the agent with the query
            events = list(
                self.runner.run(
                    user_id="price_user",
                    session_id=self.session_id,
                    new_message=user_message,
                )
            )

            # Extract the response from the events
            response_text = ""
            for event in events:
                if hasattr(event, "response") and hasattr(event.response, "text"):
                    response_text = event.response.text
                    break
                elif hasattr(event, "content") and isinstance(event.content, str):
                    response_text = event.content
                    break

            # For now, return a structured response
            # In production, you'd parse the AI response and extract structured data
            return {
                "suggested_price_range": {
                    "min": 0.0,
                    "max": 0.0,
                    "recommended": 0.0,
                },  # Would be parsed from AI response
                "market_analysis": {
                    "average_price": 0.0,
                    "price_trend": "stable",
                    "competition_level": "medium",
                },
                "reasoning": response_text or "Price analysis completed successfully.",
                "similar_listings": [],  # Would be populated with actual similar listings
                "confidence_score": 0.7,  # Would be calculated based on data quality
            }

        except Exception as e:
            return {
                "suggested_price_range": {"min": 0.0, "max": 0.0, "recommended": 0.0},
                "market_analysis": {
                    "average_price": 0.0,
                    "price_trend": "unknown",
                    "competition_level": "unknown",
                },
                "reasoning": f"Price suggestion error: {str(e)}",
                "similar_listings": [],
                "confidence_score": 0.0,
            }


# Factory function for easy agent creation
def create_price_suggestion_agent(
    model: str = "gemini-2.0-flash-exp",
) -> PriceSuggestionAgent:
    """Create a new price suggestion agent instance."""
    return PriceSuggestionAgent(model=model)


# For ADK CLI compatibility - create a simple agent that can be loaded
if ADK_AVAILABLE:
    try:
        # Create a basic ADK agent for CLI testing
        price_suggestion_root_agent = Agent(
            model="gemini-2.0-flash-exp",
            name="konnect_price_suggestion_agent",
            instruction="""You are a price suggestion agent for Konnect, a campus marketplace platform.
            Your role is to analyze market data and suggest optimal pricing for sellers.

            Available tools:
            - get_similar_listings(title, category, brand): Find similar items for comparison
            - get_market_price_stats(category): Get market price statistics
            - analyze_price_trends(category): Analyze price trends and competition""",
            tools=[
                get_similar_listings,
                get_market_price_stats,
                analyze_price_trends,
            ],
        )
    except Exception as e:
        print(f"Warning: Could not create ADK price suggestion agent: {e}")
        price_suggestion_root_agent = None
else:
    price_suggestion_root_agent = None
