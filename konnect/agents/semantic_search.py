"""
Semantic Search Agent for Konnect Campus Marketplace

This module implements a semantic search agent that provides intelligent
search capabilities using natural language queries.
"""

import os
import sys
import time
from typing import Any, Dict, List

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


def search_listings_by_keywords(
    keywords: List[str], max_results: int = 20
) -> List[Dict[str, Any]]:
    """Search listings by keywords using database queries.

    Args:
        keywords: List of keywords to search for
        max_results: Maximum number of results to return

    Returns:
        List of matching listings with details
    """
    db = SessionLocal()
    try:
        # Get all active listings
        listings = crud.get_listings(db, limit=max_results * 2)  # Get more to filter

        # Simple keyword matching (in production, you'd use more sophisticated text search)
        results = []
        for listing in listings:
            # Check if any keyword matches title, description, or category
            listing_text = f"{listing.title} {listing.description or ''} {listing.category or ''}".lower()

            matched_keywords = []
            for keyword in keywords:
                if keyword.lower() in listing_text:
                    matched_keywords.append(keyword)

            if matched_keywords:
                # Get seller and marketplace info
                seller = crud.get_user(db, listing.user_id)
                marketplace = crud.get_marketplace(db, listing.marketplace_id)

                results.append(
                    {
                        "listing_id": listing.id,
                        "title": listing.title,
                        "description": listing.description,
                        "price": listing.price,
                        "category": listing.category,
                        "seller_username": seller.username if seller else "Unknown",
                        "marketplace_name": marketplace.name
                        if marketplace
                        else "Unknown",
                        "matched_keywords": matched_keywords,
                        "created_at": listing.created_at.isoformat(),
                    }
                )

        # Sort by number of matched keywords and return top results
        results.sort(key=lambda x: len(x["matched_keywords"]), reverse=True)
        return results[:max_results]

    finally:
        db.close()


def get_listings_by_category(
    category: str, max_results: int = 20
) -> List[Dict[str, Any]]:
    """Get listings by category.

    Args:
        category: Category to search in
        max_results: Maximum number of results to return

    Returns:
        List of listings in the specified category
    """
    db = SessionLocal()
    try:
        listings = crud.get_listings(db, category=category, limit=max_results)

        results = []
        for listing in listings:
            seller = crud.get_user(db, listing.user_id)
            marketplace = crud.get_marketplace(db, listing.marketplace_id)

            results.append(
                {
                    "listing_id": listing.id,
                    "title": listing.title,
                    "description": listing.description,
                    "price": listing.price,
                    "category": listing.category,
                    "seller_username": seller.username if seller else "Unknown",
                    "marketplace_name": marketplace.name if marketplace else "Unknown",
                    "created_at": listing.created_at.isoformat(),
                }
            )

        return results

    finally:
        db.close()


def get_listings_by_price_range(
    min_price: float, max_price: float, max_results: int = 20
) -> List[Dict[str, Any]]:
    """Get listings within a price range.

    Args:
        min_price: Minimum price
        max_price: Maximum price
        max_results: Maximum number of results to return

    Returns:
        List of listings within the price range
    """
    db = SessionLocal()
    try:
        # Get all listings and filter by price
        listings = crud.get_listings(db, limit=max_results * 2)

        results = []
        for listing in listings:
            if min_price <= listing.price <= max_price:
                seller = crud.get_user(db, listing.user_id)
                marketplace = crud.get_marketplace(db, listing.marketplace_id)

                results.append(
                    {
                        "listing_id": listing.id,
                        "title": listing.title,
                        "description": listing.description,
                        "price": listing.price,
                        "category": listing.category,
                        "seller_username": seller.username if seller else "Unknown",
                        "marketplace_name": marketplace.name
                        if marketplace
                        else "Unknown",
                        "created_at": listing.created_at.isoformat(),
                    }
                )

        return results[:max_results]

    finally:
        db.close()


class SemanticSearchAgent:
    """AI-powered semantic search agent for the Konnect campus marketplace."""

    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """Initialize the semantic search agent."""
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
            # Create the agent using ADK best practices
            self.agent = Agent(
                model=self.model,
                name="konnect_semantic_search_agent",
                instruction="""You are a semantic search agent for Konnect, a campus marketplace platform.
                Your role is to interpret natural language queries and find the most relevant listings.

                Guidelines:
                - Understand the intent behind user queries (e.g., "cheap textbooks" = low-priced books)
                - Extract key concepts, categories, price ranges, and conditions from queries
                - Use the available tools to search the marketplace
                - Provide explanations for why listings match the query
                - Consider synonyms and related terms
                - Prioritize student-friendly items and budgets
                - Format results clearly with relevance scores

                Available Tools:
                1. search_listings_by_keywords(keywords, max_results) - Search by keywords
                2. get_listings_by_category(category, max_results) - Search by category
                3. get_listings_by_price_range(min_price, max_price, max_results) - Search by price

                When processing a search query:
                1. Extract keywords, categories, and price ranges
                2. Use appropriate tools to find matching listings
                3. Calculate relevance scores based on match quality
                4. Provide explanations for matches
                5. Return structured results with metadata""",
                tools=[
                    search_listings_by_keywords,
                    get_listings_by_category,
                    get_listings_by_price_range,
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
                    temperature=0.3,  # Lower temperature for more consistent search results
                    top_p=0.8,
                    max_output_tokens=1500,
                ),
            )

            # Create session service and runner
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="konnect_semantic_search",
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

    def search(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """Perform semantic search on the query.

        Args:
            query: Natural language search query
            max_results: Maximum number of results to return

        Returns:
            Dictionary containing search results and metadata
        """
        start_time = time.time()

        if not ADK_AVAILABLE:
            # Mock response when ADK is not available
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "search_time_ms": int((time.time() - start_time) * 1000),
                "explanation": "Mock search: Google ADK not available. In a real environment, this would provide semantic search results.",
            }

        if not self.runner:
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "search_time_ms": int((time.time() - start_time) * 1000),
                "explanation": "Sorry, I couldn't initialize the search system.",
            }

        try:
            # Create a user message content
            user_message = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"Search for: {query}. Return up to {max_results} results."
                    )
                ],
            )

            # Create a session if we don't have one
            if not self.session_id and self.session_service:
                import asyncio

                try:
                    session = asyncio.run(
                        self.session_service.create_session(
                            app_name="konnect_semantic_search",
                            user_id="search_user",
                        )
                    )
                    self.session_id = session.id
                except RuntimeError:
                    # If we're already in an event loop, create session synchronously
                    import nest_asyncio

                    nest_asyncio.apply()
                    session = asyncio.run(
                        self.session_service.create_session(
                            app_name="konnect_semantic_search",
                            user_id="search_user",
                        )
                    )
                    self.session_id = session.id

            # Run the agent with the query
            events = list(
                self.runner.run(
                    user_id="search_user",
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
            search_time_ms = int((time.time() - start_time) * 1000)

            return {
                "query": query,
                "results": [],  # Would be populated with parsed results
                "total_found": 0,  # Would be calculated from actual results
                "search_time_ms": search_time_ms,
                "explanation": response_text or "Search completed successfully.",
            }

        except Exception as e:
            search_time_ms = int((time.time() - start_time) * 1000)
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "search_time_ms": search_time_ms,
                "explanation": f"Search error: {str(e)}",
            }


# Factory function for easy agent creation
def create_semantic_search_agent(
    model: str = "gemini-2.0-flash-exp",
) -> SemanticSearchAgent:
    """Create a new semantic search agent instance."""
    return SemanticSearchAgent(model=model)


# For ADK CLI compatibility - create a simple agent that can be loaded
if ADK_AVAILABLE:
    try:
        # Create a basic ADK agent for CLI testing
        semantic_search_root_agent = Agent(
            model="gemini-2.0-flash-exp",
            name="konnect_semantic_search_agent",
            instruction="""You are a semantic search agent for Konnect, a campus marketplace platform.
            Your role is to interpret natural language queries and find the most relevant listings.

            Available tools:
            - search_listings_by_keywords(keywords, max_results): Search by keywords
            - get_listings_by_category(category, max_results): Search by category
            - get_listings_by_price_range(min_price, max_price, max_results): Search by price""",
            tools=[
                search_listings_by_keywords,
                get_listings_by_category,
                get_listings_by_price_range,
            ],
        )
    except Exception as e:
        print(f"Warning: Could not create ADK semantic search agent: {e}")
        semantic_search_root_agent = None
else:
    semantic_search_root_agent = None
