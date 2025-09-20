"""
Description Generation Agent for Konnect Campus Marketplace

This module implements a description generation agent that creates compelling
and detailed product descriptions for sellers.
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


def get_category_examples(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get example descriptions for a category.

    Args:
        category: Category to get examples for

    Returns:
        List of example descriptions from similar listings
    """
    db = SessionLocal()
    try:
        if category:
            listings = crud.get_listings(db, category=category, limit=20)
        else:
            listings = crud.get_listings(db, limit=50)

        examples = []
        for listing in listings:
            if (
                listing.description and len(listing.description) > 50
            ):  # Only include substantial descriptions
                examples.append(
                    {
                        "title": listing.title,
                        "description": listing.description,
                        "category": listing.category,
                        "price": listing.price,
                    }
                )

        return examples[:10]  # Return top 10 examples

    finally:
        db.close()


def get_popular_keywords(category: Optional[str] = None) -> List[str]:
    """Get popular keywords for a category.

    Args:
        category: Category to analyze

    Returns:
        List of popular keywords
    """
    db = SessionLocal()
    try:
        if category:
            listings = crud.get_listings(db, category=category, limit=100)
        else:
            listings = crud.get_listings(db, limit=200)

        # Simple keyword extraction from titles and descriptions
        keywords = []
        for listing in listings:
            if listing.title:
                keywords.extend(listing.title.lower().split())
            if listing.description:
                keywords.extend(listing.description.lower().split())

        # Count keyword frequency
        keyword_counts = {}
        for keyword in keywords:
            # Filter out common words and short words
            if len(keyword) > 3 and keyword not in [
                "the",
                "and",
                "for",
                "with",
                "this",
                "that",
                "from",
                "they",
                "have",
                "been",
                "were",
                "said",
                "each",
                "which",
                "their",
                "time",
                "will",
                "about",
                "there",
                "could",
                "other",
                "after",
                "first",
                "well",
                "also",
                "where",
                "much",
                "some",
                "very",
                "when",
                "here",
                "just",
                "into",
                "over",
                "think",
                "more",
                "your",
                "work",
                "know",
                "way",
                "may",
                "say",
                "use",
                "her",
                "than",
                "call",
                "its",
                "who",
                "oil",
                "sit",
                "now",
                "find",
                "long",
                "down",
                "day",
                "did",
                "get",
                "come",
                "made",
                "may",
                "part",
            ]:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        # Sort by frequency and return top keywords
        popular_keywords = sorted(
            keyword_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [keyword for keyword, count in popular_keywords[:20]]

    finally:
        db.close()


def analyze_description_quality(description: str) -> Dict[str, Any]:
    """Analyze the quality of a description.

    Args:
        description: Description to analyze

    Returns:
        Dictionary with quality metrics
    """
    if not description:
        return {
            "word_count": 0,
            "readability_score": 0.0,
            "seo_score": 0.0,
            "has_keywords": False,
            "suggestions": ["Description is empty"],
        }

    words = description.split()
    word_count = len(words)

    # Simple readability score based on word length and sentence structure
    avg_word_length = sum(len(word) for word in words) / word_count if words else 0
    sentences = description.split(".")
    avg_sentence_length = word_count / len(sentences) if sentences else 0

    # Calculate readability score (simplified Flesch Reading Ease approximation)
    readability_score = max(
        0, min(1, 1 - (avg_word_length - 4) / 10 - (avg_sentence_length - 15) / 20)
    )

    # Simple SEO score based on length and keyword density
    seo_score = min(1.0, word_count / 200)  # Optimal around 200+ words

    # Check for common keywords
    description_lower = description.lower()
    has_keywords = any(
        keyword in description_lower
        for keyword in [
            "excellent",
            "good",
            "perfect",
            "great",
            "condition",
            "quality",
            "like new",
            "barely used",
        ]
    )

    suggestions = []
    if word_count < 50:
        suggestions.append("Consider adding more details about the item")
    if word_count > 500:
        suggestions.append("Description might be too long - consider shortening")
    if not has_keywords:
        suggestions.append("Consider adding descriptive keywords about condition")
    if readability_score < 0.5:
        suggestions.append("Consider simplifying sentence structure")

    return {
        "word_count": word_count,
        "readability_score": round(readability_score, 2),
        "seo_score": round(seo_score, 2),
        "has_keywords": has_keywords,
        "suggestions": suggestions,
    }


class DescriptionGenerationAgent:
    """AI-powered description generation agent for the Konnect campus marketplace."""

    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """Initialize the description generation agent."""
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
                name="konnect_description_generation_agent",
                instruction="""You are a description generation agent for Konnect, a campus marketplace platform.
                Your role is to create compelling and detailed product descriptions for sellers.

                Guidelines:
                - Write clear, engaging descriptions that highlight key features
                - Use appropriate tone based on target audience (students, general public)
                - Include relevant keywords for better searchability
                - Mention condition, brand, and unique selling points
                - Keep descriptions informative but not overly long
                - Use active voice and descriptive language
                - Include practical benefits and use cases
                - Consider campus/student context when relevant

                Available Tools:
                1. get_category_examples(category) - Get example descriptions from similar listings
                2. get_popular_keywords(category) - Get popular keywords for the category
                3. analyze_description_quality(description) - Analyze description quality metrics

                When generating descriptions:
                1. Analyze the item title and key features
                2. Look at examples from similar listings
                3. Incorporate popular keywords naturally
                4. Create multiple variations with different tones
                5. Ensure descriptions are SEO-friendly and readable
                6. Provide quality scores and suggestions""",
                tools=[
                    get_category_examples,
                    get_popular_keywords,
                    analyze_description_quality,
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
                    temperature=0.7,  # Higher creativity for description generation
                    top_p=0.9,
                    max_output_tokens=1000,
                ),
            )

            # Create session service and runner
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="konnect_description_generation",
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

    def generate_description(
        self,
        title: str,
        category: Optional[str] = None,
        condition: Optional[str] = None,
        brand: Optional[str] = None,
        key_features: List[str] = None,
        target_audience: Optional[str] = None,
        tone: str = "professional",
    ) -> Dict[str, Any]:
        """Generate product description.

        Args:
            title: Product title
            category: Product category
            condition: Item condition
            brand: Item brand
            key_features: List of key features
            target_audience: Target audience (students, general, etc.)
            tone: Writing tone (professional, casual, friendly)

        Returns:
            Dictionary containing generated descriptions and analysis
        """
        if key_features is None:
            key_features = []

        if not ADK_AVAILABLE:
            # Mock response when ADK is not available
            mock_description = f"This {title.lower()} is in excellent condition and perfect for students. "
            if condition:
                mock_description += f"The item is {condition} and well-maintained. "
            if brand:
                mock_description += f"From the trusted brand {brand}, "
            mock_description += "this item offers great value and functionality. Ideal for campus life and academic needs."

            return {
                "generated_description": mock_description,
                "alternative_descriptions": [
                    f"High-quality {title.lower()} in great condition. Perfect for students looking for reliable equipment.",
                    f"Excellent {title.lower()} - well-cared for and ready to use. Great value for money.",
                ],
                "suggested_keywords": [
                    "excellent",
                    "condition",
                    "students",
                    "quality",
                    "value",
                ],
                "seo_score": 0.7,
                "readability_score": 0.8,
            }

        if not self.runner:
            return {
                "generated_description": "",
                "alternative_descriptions": [],
                "suggested_keywords": [],
                "seo_score": 0.0,
                "readability_score": 0.0,
            }

        try:
            # Create a user message content
            query_parts = [f"Generate a description for: {title}"]
            if category:
                query_parts.append(f"Category: {category}")
            if condition:
                query_parts.append(f"Condition: {condition}")
            if brand:
                query_parts.append(f"Brand: {brand}")
            if key_features:
                query_parts.append(f"Key features: {', '.join(key_features)}")
            if target_audience:
                query_parts.append(f"Target audience: {target_audience}")
            query_parts.append(f"Tone: {tone}")

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
                            app_name="konnect_description_generation",
                            user_id="description_user",
                        )
                    )
                    self.session_id = session.id
                except RuntimeError:
                    # If we're already in an event loop, create session synchronously
                    import nest_asyncio

                    nest_asyncio.apply()
                    session = asyncio.run(
                        self.session_service.create_session(
                            app_name="konnect_description_generation",
                            user_id="description_user",
                        )
                    )
                    self.session_id = session.id

            # Run the agent with the query
            events = list(
                self.runner.run(
                    user_id="description_user",
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
                "generated_description": response_text
                or "Description generation completed successfully.",
                "alternative_descriptions": [],  # Would be populated with alternative versions
                "suggested_keywords": [],  # Would be extracted from the generated description
                "seo_score": 0.7,  # Would be calculated based on content analysis
                "readability_score": 0.8,  # Would be calculated using readability metrics
            }

        except Exception:
            return {
                "generated_description": "",
                "alternative_descriptions": [],
                "suggested_keywords": [],
                "seo_score": 0.0,
                "readability_score": 0.0,
            }


# Factory function for easy agent creation
def create_description_generation_agent(
    model: str = "gemini-2.0-flash-exp",
) -> DescriptionGenerationAgent:
    """Create a new description generation agent instance."""
    return DescriptionGenerationAgent(model=model)


# For ADK CLI compatibility - create a simple agent that can be loaded
if ADK_AVAILABLE:
    try:
        # Create a basic ADK agent for CLI testing
        description_generation_root_agent = Agent(
            model="gemini-2.0-flash-exp",
            name="konnect_description_generation_agent",
            instruction="""You are a description generation agent for Konnect, a campus marketplace platform.
            Your role is to create compelling and detailed product descriptions for sellers.

            Available tools:
            - get_category_examples(category): Get example descriptions from similar listings
            - get_popular_keywords(category): Get popular keywords for the category
            - analyze_description_quality(description): Analyze description quality metrics""",
            tools=[
                get_category_examples,
                get_popular_keywords,
                analyze_description_quality,
            ],
        )
    except Exception as e:
        print(f"Warning: Could not create ADK description generation agent: {e}")
        description_generation_root_agent = None
else:
    description_generation_root_agent = None
