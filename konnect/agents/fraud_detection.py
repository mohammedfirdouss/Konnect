"""
Fraud Detection Agent for Konnect Campus Marketplace

This module implements a fraud detection agent that analyzes users and listings
for suspicious activity patterns.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add the project root to the Python path for database access
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Local imports
from konnect import crud, models  # noqa: E402
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


def analyze_user_activity(user_id: int) -> Dict[str, Any]:
    """Analyze user activity for suspicious patterns.

    Args:
        user_id: User ID to analyze

    Returns:
        Dictionary with user activity analysis
    """
    db = SessionLocal()
    try:
        user = crud.get_user(db, user_id)
        if not user:
            return {"error": "User not found"}

        # Get user's listings
        listings = crud.get_listings(db, limit=1000)
        user_listings = [listing for listing in listings if listing.user_id == user_id]

        # Get user's orders
        orders = (
            db.query(models.Order)
            .filter(
                (models.Order.buyer_id == user_id) | (models.Order.seller_id == user_id)
            )
            .all()
        )

        # Get user's reviews
        reviews_given = (
            db.query(models.UserReview)
            .filter(models.UserReview.reviewer_id == user_id)
            .all()
        )
        reviews_received = (
            db.query(models.UserReview)
            .filter(models.UserReview.reviewed_user_id == user_id)
            .all()
        )

        # Analyze patterns
        analysis = {
            "user_id": user_id,
            "account_age_days": (datetime.now() - user.created_at).days,
            "total_listings": len(user_listings),
            "total_orders": len(orders),
            "reviews_given": len(reviews_given),
            "reviews_received": len(reviews_received),
            "is_verified_seller": user.is_verified_seller,
            "risk_factors": [],
            "risk_score": 0.0,
        }

        # Calculate risk factors
        risk_factors = []
        risk_score = 0.0

        # New account with many listings
        if analysis["account_age_days"] < 7 and analysis["total_listings"] > 10:
            risk_factors.append("New account with many listings")
            risk_score += 0.3

        # No reviews received despite many listings
        if analysis["total_listings"] > 5 and analysis["reviews_received"] == 0:
            risk_factors.append("No reviews despite multiple listings")
            risk_score += 0.2

        # Suspicious pricing patterns
        if user_listings:
            prices = [listing.price for listing in user_listings]
            avg_price = sum(prices) / len(prices)
            if avg_price > 1000:  # High-value items
                risk_factors.append("High-value listings")
                risk_score += 0.1

        # Unverified seller with many listings
        if not user.is_verified_seller and analysis["total_listings"] > 20:
            risk_factors.append("Unverified seller with many listings")
            risk_score += 0.2

        analysis["risk_factors"] = risk_factors
        analysis["risk_score"] = min(1.0, risk_score)

        return analysis

    finally:
        db.close()


def analyze_listing_patterns(listing_id: int) -> Dict[str, Any]:
    """Analyze listing for suspicious patterns.

    Args:
        listing_id: Listing ID to analyze

    Returns:
        Dictionary with listing analysis
    """
    db = SessionLocal()
    try:
        listing = crud.get_listing(db, listing_id)
        if not listing:
            return {"error": "Listing not found"}

        seller = crud.get_user(db, listing.user_id)

        # Get seller's other listings
        seller_listings = crud.get_listings(db, limit=1000)
        seller_listings = [
            listing_item
            for listing_item in seller_listings
            if listing_item.user_id == listing.user_id
        ]

        analysis = {
            "listing_id": listing_id,
            "title": listing.title,
            "price": listing.price,
            "category": listing.category,
            "seller_id": listing.user_id,
            "seller_username": seller.username if seller else "Unknown",
            "seller_total_listings": len(seller_listings),
            "seller_is_verified": seller.is_verified_seller if seller else False,
            "risk_factors": [],
            "risk_score": 0.0,
        }

        # Calculate risk factors
        risk_factors = []
        risk_score = 0.0

        # Suspicious title patterns
        title_lower = listing.title.lower()
        suspicious_keywords = [
            "urgent",
            "quick sale",
            "must sell",
            "asap",
            "cash only",
            "no questions",
        ]
        if any(keyword in title_lower for keyword in suspicious_keywords):
            risk_factors.append("Suspicious keywords in title")
            risk_score += 0.2

        # Unusually high or low price
        if listing.price > 5000:
            risk_factors.append("Unusually high price")
            risk_score += 0.1
        elif listing.price < 1:
            risk_factors.append("Unusually low price")
            risk_score += 0.1

        # Generic or vague description
        if not listing.description or len(listing.description) < 20:
            risk_factors.append("Vague or missing description")
            risk_score += 0.2

        # Unverified seller
        if not seller or not seller.is_verified_seller:
            risk_factors.append("Unverified seller")
            risk_score += 0.1

        analysis["risk_factors"] = risk_factors
        analysis["risk_score"] = min(1.0, risk_score)

        return analysis

    finally:
        db.close()


def get_recent_fraud_indicators() -> List[Dict[str, Any]]:
    """Get recent fraud indicators across the platform.

    Returns:
        List of recent fraud indicators
    """
    db = SessionLocal()
    try:
        # Get recent users with suspicious patterns
        recent_users = (
            db.query(models.User)
            .filter(models.User.created_at >= datetime.now() - timedelta(days=30))
            .all()
        )

        indicators = []

        for user in recent_users:
            # Check for new users with many listings
            user_listings = [
                listing
                for listing in crud.get_listings(db, limit=1000)
                if listing.user_id == user.id
            ]

            if len(user_listings) > 10:  # Threshold for suspicious activity
                indicators.append(
                    {
                        "type": "user",
                        "entity_id": user.id,
                        "reason": "New user with many listings",
                        "risk_score": 0.7,
                        "created_at": user.created_at.isoformat(),
                    }
                )

        # Get recent listings with suspicious patterns
        recent_listings = crud.get_listings(db, limit=100)

        for listing in recent_listings:
            # Check for suspicious keywords
            title_lower = listing.title.lower()
            if any(
                keyword in title_lower
                for keyword in ["urgent", "quick sale", "must sell"]
            ):
                indicators.append(
                    {
                        "type": "listing",
                        "entity_id": listing.id,
                        "reason": "Suspicious keywords in title",
                        "risk_score": 0.5,
                        "created_at": listing.created_at.isoformat(),
                    }
                )

        # Sort by risk score and return top indicators
        indicators.sort(key=lambda x: x["risk_score"], reverse=True)
        return indicators[:20]

    finally:
        db.close()


class FraudDetectionAgent:
    """AI-powered fraud detection agent for the Konnect campus marketplace."""

    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """Initialize the fraud detection agent."""
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
                name="konnect_fraud_detection_agent",
                instruction="""You are a fraud detection agent for Konnect, a campus marketplace platform.
                Your role is to analyze users and listings for suspicious activity patterns.

                Guidelines:
                - Identify patterns that suggest fraudulent activity
                - Consider account age, listing patterns, pricing, and user behavior
                - Provide risk scores and detailed explanations
                - Flag suspicious keywords, pricing patterns, and user behavior
                - Consider campus marketplace context and student behavior
                - Provide actionable insights for admin review

                Available Tools:
                1. analyze_user_activity(user_id) - Analyze user for suspicious patterns
                2. analyze_listing_patterns(listing_id) - Analyze listing for fraud indicators
                3. get_recent_fraud_indicators() - Get recent fraud indicators across platform

                When analyzing for fraud:
                1. Look for patterns that deviate from normal student marketplace behavior
                2. Consider multiple factors together (account age, activity, pricing, etc.)
                3. Provide clear risk scores and explanations
                4. Flag items for admin review when appropriate
                5. Consider false positives and legitimate student behavior""",
                tools=[
                    analyze_user_activity,
                    analyze_listing_patterns,
                    get_recent_fraud_indicators,
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
                    temperature=0.2,  # Low temperature for consistent fraud detection
                    top_p=0.7,
                    max_output_tokens=1000,
                ),
            )

            # Create session service and runner
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="konnect_fraud_detection",
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

    def detect_fraud(self, entity_type: str, entity_id: int) -> Dict[str, Any]:
        """Detect fraud for a specific entity.

        Args:
            entity_type: Type of entity ("user" or "listing")
            entity_id: ID of the entity to analyze

        Returns:
            Dictionary containing fraud detection results
        """
        if not ADK_AVAILABLE:
            # Mock response when ADK is not available
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "risk_score": 0.3,
                "risk_level": "low",
                "flagged_reasons": ["Mock analysis: Google ADK not available"],
                "detection_method": "mock",
                "confidence": 0.5,
                "recommendations": ["Manual review recommended"],
            }

        if not self.runner:
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "risk_score": 0.0,
                "risk_level": "unknown",
                "flagged_reasons": ["Analysis system unavailable"],
                "detection_method": "error",
                "confidence": 0.0,
                "recommendations": [],
            }

        try:
            # Create a user message content
            query = f"Analyze {entity_type} with ID {entity_id} for fraud indicators"
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
                            app_name="konnect_fraud_detection",
                            user_id="fraud_user",
                        )
                    )
                    self.session_id = session.id
                except RuntimeError:
                    # If we're already in an event loop, create session synchronously
                    import nest_asyncio

                    nest_asyncio.apply()
                    session = asyncio.run(
                        self.session_service.create_session(
                            app_name="konnect_fraud_detection",
                            user_id="fraud_user",
                        )
                    )
                    self.session_id = session.id

            # Run the agent with the query
            events = list(
                self.runner.run(
                    user_id="fraud_user",
                    session_id=self.session_id,
                    new_message=user_message,
                )
            )

            # Extract the response from the events
            for event in events:
                if hasattr(event, "response") and hasattr(event.response, "text"):
                    break
                elif hasattr(event, "content") and isinstance(event.content, str):
                    break

            # For now, return a structured response
            # In production, you'd parse the AI response and extract structured data
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "risk_score": 0.3,  # Would be calculated from analysis
                "risk_level": "low",  # Would be determined from risk score
                "flagged_reasons": [
                    "Analysis completed"
                ],  # Would be extracted from AI response
                "detection_method": "ai_analysis",
                "confidence": 0.7,  # Would be calculated based on data quality
                "recommendations": ["Continue monitoring"],  # Would be generated by AI
            }

        except Exception as e:
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "risk_score": 0.0,
                "risk_level": "unknown",
                "flagged_reasons": [f"Analysis error: {str(e)}"],
                "detection_method": "error",
                "confidence": 0.0,
                "recommendations": [],
            }

    def get_fraud_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent fraud detection reports.

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of fraud detection reports
        """
        if not ADK_AVAILABLE:
            # Mock response when ADK is not available
            return [
                {
                    "id": 1,
                    "entity_type": "user",
                    "entity_id": 123,
                    "risk_score": 0.7,
                    "risk_level": "high",
                    "flagged_reasons": ["New account with many listings"],
                    "detection_method": "mock",
                    "confidence": 0.8,
                    "created_at": datetime.now().isoformat(),
                    "status": "pending",
                    "admin_notes": None,
                }
            ]

        # Get recent fraud indicators
        indicators = get_recent_fraud_indicators()

        # Convert to report format
        reports = []
        for i, indicator in enumerate(indicators[:limit]):
            reports.append(
                {
                    "id": i + 1,
                    "entity_type": indicator["type"],
                    "entity_id": indicator["entity_id"],
                    "risk_score": indicator["risk_score"],
                    "risk_level": "high"
                    if indicator["risk_score"] > 0.7
                    else "medium"
                    if indicator["risk_score"] > 0.4
                    else "low",
                    "flagged_reasons": [indicator["reason"]],
                    "detection_method": "pattern_analysis",
                    "confidence": 0.8,
                    "created_at": indicator["created_at"],
                    "status": "pending",
                    "admin_notes": None,
                }
            )

        return reports


# Factory function for easy agent creation
def create_fraud_detection_agent(
    model: str = "gemini-2.0-flash-exp",
) -> FraudDetectionAgent:
    """Create a new fraud detection agent instance."""
    return FraudDetectionAgent(model=model)


# For ADK CLI compatibility - create a simple agent that can be loaded
if ADK_AVAILABLE:
    try:
        # Create a basic ADK agent for CLI testing
        fraud_detection_root_agent = Agent(
            model="gemini-2.0-flash-exp",
            name="konnect_fraud_detection_agent",
            instruction="""You are a fraud detection agent for Konnect, a campus marketplace platform.
            Your role is to analyze users and listings for suspicious activity patterns.

            Available tools:
            - analyze_user_activity(user_id): Analyze user for suspicious patterns
            - analyze_listing_patterns(listing_id): Analyze listing for fraud indicators
            - get_recent_fraud_indicators(): Get recent fraud indicators across platform""",
            tools=[
                analyze_user_activity,
                analyze_listing_patterns,
                get_recent_fraud_indicators,
            ],
        )
    except Exception as e:
        print(f"Warning: Could not create ADK fraud detection agent: {e}")
        fraud_detection_root_agent = None
else:
    fraud_detection_root_agent = None
