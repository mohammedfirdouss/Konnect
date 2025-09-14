"""
Recommendation Agent for Konnect Campus Marketplace

This module implements a recommendation agent that provides personalized
suggestions for students on the campus marketplace platform using Google ADK.
"""

from typing import Any, Dict, List, Optional

from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types


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
            "popularity_score": 95
        },
        {
            "id": 2,
            "title": "Calculus Textbook (Stewart)",
            "price": 45.0,
            "category": "Books",
            "description": "Latest edition, minimal highlighting",
            "popularity_score": 87
        },
        {
            "id": 3,
            "title": "IKEA Desk Lamp",
            "price": 15.0,
            "category": "Furniture",
            "description": "Perfect for dorm room study setup",
            "popularity_score": 78
        }
    ]


def search_items_by_category(category: str) -> List[Dict[str, Any]]:
    """Search for items in a specific category.

    Args:
        category: The category to search in (e.g., "Electronics", "Books", "Furniture")

    Returns:
        A list of items in the specified category.
    """
    all_items = [
        {"id": 1, "title": "MacBook Pro 13-inch", "price": 800.0, "category": "Electronics"},
        {"id": 2, "title": "iPhone 12", "price": 400.0, "category": "Electronics"},
        {"id": 3, "title": "Calculus Textbook", "price": 45.0, "category": "Books"},
        {"id": 4, "title": "Chemistry Lab Manual", "price": 25.0, "category": "Books"},
        {"id": 5, "title": "IKEA Desk Lamp", "price": 15.0, "category": "Furniture"},
        {"id": 6, "title": "Study Chair", "price": 80.0, "category": "Furniture"},
    ]

    # Filter items by category (case insensitive)
    category_lower = category.lower()
    filtered_items = [
        item for item in all_items
        if item["category"].lower() == category_lower
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
        {"id": 6, "title": "Scientific Calculator", "price": 35.0, "category": "Electronics"},
    ]

    # Filter items by price range
    filtered_items = [
        item for item in all_items
        if min_price <= item["price"] <= max_price
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
        self.agent = Agent(
            model=model,
            name="konnect_recommendation_agent",
            instruction="""
            You are a helpful recommendation agent for Konnect, a campus marketplace platform
            where students can buy and sell items to each other. Your role is to provide
            personalized recommendations based on user queries.

            Guidelines:
            - Always be helpful and student-friendly
            - Consider budget constraints - students typically have limited budgets
            - Prioritize items that are popular among students
            - Suggest alternatives when exact matches aren't available
            - Explain why you're recommending specific items
            - Use the available tools to get current marketplace data
            - Format responses in a clear, easy-to-read way
            - Always mention prices when recommending items
            - Suggest both individual items and bundles when appropriate

            When users ask for recommendations:
            1. Use get_popular_items() to see what's trending
            2. Use search_items_by_category() for specific categories
            3. Use get_price_range_items() for budget-conscious searches
            4. Provide 3-5 recommendations with explanations
            5. Include prices and brief descriptions
            """,
            tools=[
                get_popular_items,
                search_items_by_category,
                get_price_range_items,
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

        # Create a runner to execute the agent
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name="konnect_recommendations",
            agent=self.agent,
            session_service=self.session_service,
        )

        # Create a session for interactions
        self.session_id = self.session_service.create_session(
            app_name="konnect_recommendations",
            user_id="default_user",
        ).id

    def get_recommendations(self, query: str) -> str:
        """Get recommendations based on user query.

        Args:
            query: User's request for recommendations

        Returns:
            AI-generated recommendations as a string
        """
        try:
            # Create a user message content
            user_message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=query)],
            )

            # Run the agent with the query
            events = list(self.runner.run(
                user_id="default_user",
                session_id=self.session_id,
                new_message=user_message,
            ))

            # Extract the text response from the events
            for event in events:
                if hasattr(event, 'response') and hasattr(event.response, 'text'):
                    return event.response.text
                elif hasattr(event, 'content') and isinstance(event.content, str):
                    return event.content

            return "I apologize, but I couldn't generate recommendations at this time."

        except Exception as e:
            return f"Sorry, I encountered an error while generating recommendations: {str(e)}"

    def get_category_recommendations(self, category: str, budget: Optional[float] = None) -> str:
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


# Factory function for easy agent creation
def create_recommendation_agent(model: str = "gemini-2.0-flash-exp") -> RecommendationAgent:
    """Create a new recommendation agent instance.

    Args:
        model: The Google GenAI model to use

    Returns:
        A configured RecommendationAgent instance
    """
    return RecommendationAgent(model=model)
