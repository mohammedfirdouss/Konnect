"""
Recommendation Agent for Konnect Campus Marketplace

This module implements a recommendation agent that provides personalized
suggestions for students on the campus marketplace platform using Google ADK.
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


def get_user_activity(user_id: int) -> Dict[str, Any]:
    """Get user activity and purchase history from the database.

    This function queries the application's database to fetch comprehensive
    user activity data including purchase history, browsing patterns, and
    preferences to help the agent provide personalized recommendations.

    Args:
        user_id: The ID of the user to get activity for

    Returns:
        A dictionary containing user activity summary with:
        - total_purchases: Number of completed purchases
        - total_spent: Total amount spent on purchases
        - recent_purchases: List of recent purchase records
        - recent_activities: List of recent user activities (views, searches)
        - favorite_categories: Most frequently purchased categories
        - recent_views: Recent items viewed by the user
        - recent_searches: Recent search queries by the user
    """
    db = SessionLocal()
    try:
        return get_user_activity_with_db(db, user_id)
    finally:
        db.close()


def get_user_activity_with_db(db, user_id: int) -> Dict[str, Any]:
    """Get user activity with a provided database session.

    This version is more testable as it accepts a database session.
    """
    activity_data = crud.get_user_activity_summary(db, user_id)

    # Convert database objects to simple dictionaries for the agent
    result = {
        "user_id": activity_data["user_id"],
        "total_purchases": activity_data["total_purchases"],
        "total_spent": activity_data["total_spent"],
        "favorite_categories": activity_data["favorite_categories"],
        "recent_purchases": [
            {
                "id": p.id,
                "listing_id": p.listing_id,
                "amount": p.amount,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
            }
            for p in activity_data["recent_purchases"]
        ],
        "recent_activities": [
            {
                "activity_type": a.activity_type,
                "target_id": a.target_id,
                "target_type": a.target_type,
                "created_at": a.created_at.isoformat(),
            }
            for a in activity_data["recent_activities"]
        ],
        "recent_views": [
            {
                "target_id": a.target_id,
                "target_type": a.target_type,
                "created_at": a.created_at.isoformat(),
            }
            for a in activity_data["recent_views"]
        ],
        "recent_searches": [
            {
                "activity_data": a.activity_data,
                "created_at": a.created_at.isoformat(),
            }
            for a in activity_data["recent_searches"]
        ],
    }

    return result


def get_popular_items() -> List[Dict[str, Any]]:
    """Get popular items from the marketplace.

    Returns:
        A list of popular items with their details.
    """
    # Mock data for now - in a real implementation, this would query the database
    return [
        {
            "id": 1,
            "title": "MacBook Pro 13-inch (Used)",
            "price": 800.0,
            "category": "Electronics",
            "description": "Excellent condition, perfect for students",
            "popularity_score": 95,
        },
        {
            "id": 2,
            "title": "Calculus Textbook (Stewart)",
            "price": 45.0,
            "category": "Books",
            "description": "Latest edition, minimal highlighting",
            "popularity_score": 87,
        },
        {
            "id": 3,
            "title": "IKEA Desk Lamp",
            "price": 15.0,
            "category": "Furniture",
            "description": "Perfect for dorm room study setup",
            "popularity_score": 78,
        },
    ]


def search_items_by_category(category: str) -> List[Dict[str, Any]]:
    """Search for items in a specific category.

    Args:
        category: The category to search in (e.g., "Electronics", "Books", "Furniture")

    Returns:
        A list of items in the specified category.
    """
    all_items = [
        {
            "id": 1,
            "title": "MacBook Pro 13-inch",
            "price": 800.0,
            "category": "Electronics",
        },
        {"id": 2, "title": "iPhone 12", "price": 400.0, "category": "Electronics"},
        {"id": 3, "title": "Calculus Textbook", "price": 45.0, "category": "Books"},
        {"id": 4, "title": "Chemistry Lab Manual", "price": 25.0, "category": "Books"},
        {"id": 5, "title": "IKEA Desk Lamp", "price": 15.0, "category": "Furniture"},
        {"id": 6, "title": "Study Chair", "price": 80.0, "category": "Furniture"},
    ]

    # Filter items by category (case insensitive)
    category_lower = category.lower()
    filtered_items = [
        item for item in all_items if item["category"].lower() == category_lower
    ]

    return filtered_items


def get_price_range_items(min_price: float, max_price: float) -> List[Dict[str, Any]]:
    """Get items within a specific price range.

    Args:
        min_price: Minimum price filter
        max_price: Maximum price filter

    Returns:
        A list of items within the specified price range.
    """
    all_items = get_popular_items() + [
        {"id": 4, "title": "Chemistry Lab Manual", "price": 25.0, "category": "Books"},
        {"id": 5, "title": "Study Chair", "price": 80.0, "category": "Furniture"},
        {
            "id": 6,
            "title": "Scientific Calculator",
            "price": 35.0,
            "category": "Electronics",
        },
    ]

    # Filter items by price range
    filtered_items = [
        item for item in all_items if min_price <= item["price"] <= max_price
    ]

    return filtered_items


class RecommendationAgent:
    """AI-powered recommendation agent for the Konnect campus marketplace.

    This agent provides personalized recommendations based on user preferences,
    popular items, categories, and price ranges using Google ADK.
    """

    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """Initialize the recommendation agent.

        Args:
            model: The Google GenAI model to use for recommendations
        """
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
                name="konnect_recommendation_agent",
                instruction="""You are a helpful recommendation agent for Konnect,
                a campus
            marketplace platform where students can buy and sell items to each other.
            Your role is to provide personalized recommendations based on user queries
            and their activity history.

            Guidelines:
            - Always be helpful and student-friendly
            - Consider budget constraints - students typically have limited budgets
            - Prioritize items that are popular among students
            - Use user purchase history and preferences to personalize recommendations
            - Suggest alternatives when exact matches aren't available
            - Explain why you're recommending specific items
            - Use the available tools to get current marketplace data and user activity
            - Format responses in a clear, easy-to-read way
            - Always mention prices when recommending items
            - Suggest both individual items and bundles when appropriate

            Available Tools:
            1. get_popular_items() - Get trending items on the marketplace
            2. search_items_by_category(category) - Find items in specific categories
            3. get_price_range_items(min_price, max_price) - Find items within budget
            4. get_user_activity(user_id) - Get user's purchase history and preferences

            When users ask for recommendations:
            1. If you have a user_id, use get_user_activity() to understand
               their preferences
            2. Use get_popular_items() to see what's trending
            3. Use search_items_by_category() for specific categories
            4. Use get_price_range_items() for budget-conscious searches
            5. Provide 3-5 personalized recommendations with explanations
            6. Include prices and brief descriptions
            7. Reference their past purchases or interests when relevant""",
                tools=[
                    get_popular_items,
                    search_items_by_category,
                    get_price_range_items,
                    get_user_activity,
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
                    temperature=0.7,  # Balanced creativity for recommendations
                    top_p=0.9,
                    max_output_tokens=1000,
                ),
            )

            # Create session service and runner
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="konnect_recommendations",
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

    

    def get_recommendations(self, query: str) -> str:
        """Get recommendations based on user query.

        Args:
            query: User's request for recommendations

        Returns:
            AI-generated recommendations as a string
        """
        if not ADK_AVAILABLE:
            return (
                "Mock recommendation: Google ADK not available. "
                "In a real environment, this would provide personalized "
                "recommendations based on the query."
            )

        

        if not self.runner:
            return "Sorry, I couldn't initialize the recommendation system."

        try:
            # Create a user message content
            user_message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=query)],
            )

            # Create a session if we don't have one
            if not self.session_id and self.session_service:
                import asyncio

                try:
                    session = asyncio.run(
                        self.session_service.create_session(
                            app_name="konnect_recommendations",
                            user_id="default_user",
                        )
                    )
                    self.session_id = session.id
                except RuntimeError:
                    # If we're already in an event loop, create session synchronously
                    import nest_asyncio

                    nest_asyncio.apply()
                    session = asyncio.run(
                        self.session_service.create_session(
                            app_name="konnect_recommendations",
                            user_id="default_user",
                        )
                    )
                    self.session_id = session.id

            # Run the agent with the query
            events = list(
                self.runner.run(
                    user_id="default_user",
                    session_id=self.session_id,
                    new_message=user_message,
                )
            )

            # Extract the text response from the events
            for event in events:
                if hasattr(event, "response") and hasattr(event.response, "text"):
                    return event.response.text
                elif hasattr(event, "content") and isinstance(event.content, str):
                    return event.content

            return "I apologize, but I couldn't generate recommendations at this time."

        except Exception as e:
            error_msg = (
                "Sorry, I encountered an error while generating recommendations: "
                f"{str(e)}"
            )
            return error_msg

    def get_category_recommendations(
        self, category: str, budget: Optional[float] = None
    ) -> str:
        """Get recommendations for a specific category and optional budget.

        Args:
            category: The item category to search
            budget: Optional maximum budget

        Returns:
            AI-generated category-specific recommendations
        """
        query = f"I'm looking for items in the {category} category"
        if budget:
            query += f" with a budget of ${budget}"

        return self.get_recommendations(query)

    def get_budget_recommendations(self, min_price: float, max_price: float) -> str:
        """Get recommendations within a specific price range.

        Args:
            min_price: Minimum price
            max_price: Maximum price

        Returns:
            AI-generated budget-based recommendations
        """
        query = f"I'm looking for items between ${min_price} and ${max_price}"
        return self.get_recommendations(query)

    def get_personalized_recommendations(self, user_id: int, query: str = "") -> str:
        """Get personalized recommendations based on user activity.

        Args:
            user_id: The user ID to get recommendations for
            query: Optional additional query text

        Returns:
            AI-generated personalized recommendations
        """
        if query:
            full_query = (
                f"User ID {user_id}: {query}. "
                "Please provide personalized recommendations."
            )
        else:
            full_query = (
                f"User ID {user_id}: Please provide personalized recommendations "
                "based on my activity history."
            )

        return self.get_recommendations(full_query)


# Factory function for easy agent creation
def create_recommendation_agent(
    model: str = "gemini-2.0-flash-exp",
) -> RecommendationAgent:
    """Create a new recommendation agent instance.

    Args:
        model: The Google GenAI model to use

    Returns:
        A configured RecommendationAgent instance
    """
    return RecommendationAgent(model=model)


# For ADK CLI compatibility - create a simple agent that can be loaded
if ADK_AVAILABLE:
    try:
        # Create a basic ADK agent for CLI testing
        root_agent = Agent(
            model="gemini-2.0-flash-exp",
            name="konnect_recommendation_agent",
            instruction="""You are a helpful recommendation agent for Konnect, a campus
            marketplace platform. Help students find items they're looking for by
            providing
            recommendations based on categories, budgets, and popular items.

            Available tools:
            - get_popular_items(): Get trending items
            - search_items_by_category(category): Find items by category
            - get_price_range_items(min_price, max_price): Find items by price range
            - get_user_activity(user_id): Get user purchase history""",
            tools=[
                get_popular_items,
                search_items_by_category,
                get_price_range_items,
                get_user_activity,
            ],
        )
    except Exception as e:
        print(f"Warning: Could not create ADK agent: {e}")
        root_agent = None
else:
    root_agent = None
