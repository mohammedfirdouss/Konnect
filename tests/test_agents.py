"""
Tests for the Konnect agents module
"""

from unittest.mock import Mock, patch

import pytest

from konnect.agents import RecommendationAgent
from konnect.agents.recommendation import (
    create_recommendation_agent,
    get_popular_items,
    get_price_range_items,
    search_items_by_category,
)


class TestRecommendationAgentTools:
    """Test the agent tool functions."""

    def test_get_popular_items(self):
        """Test that get_popular_items returns expected data structure."""
        items = get_popular_items()

        assert isinstance(items, list)
        assert len(items) > 0

        # Check first item structure
        item = items[0]
        assert "id" in item
        assert "title" in item
        assert "price" in item
        assert "category" in item
        assert "description" in item
        assert "popularity_score" in item

        assert isinstance(item["price"], (int, float))
        assert item["price"] > 0

    def test_search_items_by_category(self):
        """Test category search functionality."""
        # Test existing category
        electronics = search_items_by_category("Electronics")
        assert isinstance(electronics, list)
        assert len(electronics) > 0
        assert all(item["category"] == "Electronics" for item in electronics)

        # Test case insensitive search
        books = search_items_by_category("books")
        assert isinstance(books, list)
        assert len(books) > 0
        assert all(item["category"] == "Books" for item in books)

        # Test non-existent category
        empty = search_items_by_category("NonExistent")
        assert isinstance(empty, list)
        assert len(empty) == 0

    def test_get_price_range_items(self):
        """Test price range filtering."""
        # Test price range that should include items
        items = get_price_range_items(10.0, 50.0)
        assert isinstance(items, list)
        assert len(items) > 0
        assert all(10.0 <= item["price"] <= 50.0 for item in items)

        # Test price range with no items
        expensive_items = get_price_range_items(10000.0, 20000.0)
        assert isinstance(expensive_items, list)
        assert len(expensive_items) == 0

        # Test edge case
        exact_price_items = get_price_range_items(45.0, 45.0)
        assert isinstance(exact_price_items, list)


class TestRecommendationAgent:
    """Test the RecommendationAgent class."""

    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        with patch("konnect.agents.recommendation.ADK_AVAILABLE", True), patch(
            "konnect.agents.recommendation.InMemorySessionService"
        ) as mock_session_service_class, patch(
            "konnect.agents.recommendation.Runner"
        ) as mock_runner_class, patch(
            "konnect.agents.recommendation.Agent"
        ) as mock_agent_class, patch(
            "asyncio.run"
        ) as mock_asyncio_run:
            mock_agent_instance = Mock()
            mock_runner_instance = Mock()
            mock_session_service_instance = Mock()
            mock_session = Mock()
            mock_session.id = "test_session_id"

            mock_asyncio_run.return_value = mock_session

            mock_agent_class.return_value = mock_agent_instance
            mock_runner_class.return_value = mock_runner_instance
            mock_session_service_instance.create_session.return_value = mock_session
            mock_session_service_class.return_value = mock_session_service_instance

            RecommendationAgent()

            # Verify Agent was called with correct parameters
            mock_agent_class.assert_called_once()
            call_args = mock_agent_class.call_args

            # Check keyword arguments
            assert call_args.kwargs["model"] == "gemini-2.0-flash-exp"
            assert call_args.kwargs["name"] == "konnect_recommendation_agent"
            assert "instruction" in call_args.kwargs
            assert "tools" in call_args.kwargs
            assert len(call_args.kwargs["tools"]) == 4  # Four tool functions

            # Verify Runner was called
            mock_runner_class.assert_called_once()
            runner_call_args = mock_runner_class.call_args
            assert runner_call_args.kwargs["app_name"] == "konnect_recommendations"
            assert runner_call_args.kwargs["agent"] == mock_agent_instance

    def test_custom_model_initialization(self):
        """Test agent initialization with custom model."""
        with patch("konnect.agents.recommendation.ADK_AVAILABLE", True), patch(
            "konnect.agents.recommendation.InMemorySessionService"
        ) as mock_session_service_class, patch(
            "konnect.agents.recommendation.Runner"
        ) as mock_runner_class, patch(
            "konnect.agents.recommendation.Agent"
        ) as mock_agent_class, patch(
            "asyncio.run"
        ) as mock_asyncio_run:
            mock_agent_instance = Mock()
            mock_runner_instance = Mock()
            mock_session_service_instance = Mock()
            mock_session = Mock()
            mock_session.id = "test_session_id"

            mock_asyncio_run.return_value = mock_session

            mock_agent_class.return_value = mock_agent_instance
            mock_runner_class.return_value = mock_runner_instance
            mock_session_service_instance.create_session.return_value = mock_session
            mock_session_service_class.return_value = mock_session_service_instance

            custom_model = "gemini-1.5-pro"
            RecommendationAgent(model=custom_model)

            call_args = mock_agent_class.call_args
            assert call_args.kwargs["model"] == custom_model

    def test_get_recommendations_success(self):
        """Test successful recommendation generation."""
        with patch("konnect.agents.recommendation.ADK_AVAILABLE", True), patch(
            "konnect.agents.recommendation.InMemorySessionService"
        ) as mock_session_service_class, patch(
            "konnect.agents.recommendation.Runner"
        ) as mock_runner_class, patch(
            "konnect.agents.recommendation.Agent"
        ) as mock_agent_class, patch(
            "asyncio.run"
        ) as mock_asyncio_run:
            mock_agent_instance = Mock()
            mock_runner_instance = Mock()
            mock_session_service_instance = Mock()
            mock_session = Mock()
            mock_session.id = "test_session_id"

            # Setup mock event with response
            mock_event = Mock()
            mock_event.response.text = "Here are some great recommendations!"

            mock_asyncio_run.return_value = mock_session
            mock_runner_instance.run.return_value = [mock_event]

            mock_agent_class.return_value = mock_agent_instance
            mock_runner_class.return_value = mock_runner_instance
            mock_session_service_instance.create_session.return_value = mock_session
            mock_session_service_class.return_value = mock_session_service_instance

            agent = RecommendationAgent()
            result = agent.get_recommendations("I need a laptop")

            assert result == "Here are some great recommendations!"
            mock_runner_instance.run.assert_called_once()

    def test_get_recommendations_error(self):
        """Test error handling in recommendation generation."""
        with patch("konnect.agents.recommendation.ADK_AVAILABLE", True), patch(
            "konnect.agents.recommendation.InMemorySessionService"
        ) as mock_session_service_class, patch(
            "konnect.agents.recommendation.Runner"
        ) as mock_runner_class, patch(
            "konnect.agents.recommendation.Agent"
        ) as mock_agent_class, patch(
            "asyncio.run"
        ) as mock_asyncio_run:
            mock_agent_instance = Mock()
            mock_runner_instance = Mock()
            mock_session_service_instance = Mock()
            mock_session = Mock()
            mock_session.id = "test_session_id"

            mock_asyncio_run.return_value = mock_session
            mock_runner_instance.run.side_effect = Exception("API Error")

            mock_agent_class.return_value = mock_agent_instance
            mock_runner_class.return_value = mock_runner_instance
            mock_session_service_instance.create_session.return_value = mock_session
            mock_session_service_class.return_value = mock_session_service_instance

            agent = RecommendationAgent()
            result = agent.get_recommendations("I need a laptop")

            assert "Sorry, I encountered an error" in result
            assert "API Error" in result

    def test_get_category_recommendations(self):
        """Test category-specific recommendations."""
        with patch("konnect.agents.recommendation.ADK_AVAILABLE", True), patch(
            "konnect.agents.recommendation.InMemorySessionService"
        ) as mock_session_service_class, patch(
            "konnect.agents.recommendation.Runner"
        ) as mock_runner_class, patch(
            "konnect.agents.recommendation.Agent"
        ) as mock_agent_class, patch(
            "asyncio.run"
        ) as mock_asyncio_run:
            mock_agent_instance = Mock()
            mock_runner_instance = Mock()
            mock_session_service_instance = Mock()
            mock_session = Mock()
            mock_session.id = "test_session_id"

            # Setup mock event with response
            mock_event = Mock()
            mock_event.response.text = "Electronics recommendations"

            mock_asyncio_run.return_value = mock_session
            mock_runner_instance.run.return_value = [mock_event]

            mock_agent_class.return_value = mock_agent_instance
            mock_runner_class.return_value = mock_runner_instance
            mock_session_service_instance.create_session.return_value = mock_session
            mock_session_service_class.return_value = mock_session_service_instance

            agent = RecommendationAgent()
            result = agent.get_category_recommendations("Electronics", 500.0)

            # Should call run with formatted query
            run_call_args = mock_runner_instance.run.call_args
            message_content = run_call_args.kwargs["new_message"]
            assert "Electronics" in str(message_content.parts[0].text)
            assert "500" in str(message_content.parts[0].text)
            assert result == "Electronics recommendations"

    def test_get_budget_recommendations(self):
        """Test budget-based recommendations."""
        with patch("konnect.agents.recommendation.ADK_AVAILABLE", True), patch(
            "konnect.agents.recommendation.InMemorySessionService"
        ) as mock_session_service_class, patch(
            "konnect.agents.recommendation.Runner"
        ) as mock_runner_class, patch(
            "konnect.agents.recommendation.Agent"
        ) as mock_agent_class, patch(
            "asyncio.run"
        ) as mock_asyncio_run:
            mock_agent_instance = Mock()
            mock_runner_instance = Mock()
            mock_session_service_instance = Mock()
            mock_session = Mock()
            mock_session.id = "test_session_id"

            # Setup mock event with response
            mock_event = Mock()
            mock_event.response.text = "Budget recommendations"

            mock_asyncio_run.return_value = mock_session
            mock_runner_instance.run.return_value = [mock_event]

            mock_agent_class.return_value = mock_agent_instance
            mock_runner_class.return_value = mock_runner_instance
            mock_session_service_instance.create_session.return_value = mock_session
            mock_session_service_class.return_value = mock_session_service_instance

            agent = RecommendationAgent()
            result = agent.get_budget_recommendations(50.0, 200.0)

            # Should call run with formatted query
            run_call_args = mock_runner_instance.run.call_args
            message_content = run_call_args.kwargs["new_message"]
            assert "$50" in str(message_content.parts[0].text)
            assert "$200" in str(message_content.parts[0].text)
            assert result == "Budget recommendations"

    def test_agent_constructor_call(self):
        with patch("konnect.agents.recommendation.ADK_AVAILABLE", True), patch(
            "konnect.agents.recommendation.InMemorySessionService"
        ) as mock_session_service_class, patch(
            "konnect.agents.recommendation.Runner"
        ), patch(
            "konnect.agents.recommendation.Agent"
        ) as mock_agent_class, patch(
            "asyncio.run"
        ) as mock_asyncio_run:
            mock_session = Mock()
            mock_session.id = "test_session_id"
            mock_asyncio_run.return_value = mock_session

            mock_session_service_instance = Mock()
            mock_session_service_instance.create_session.return_value = mock_session
            mock_session_service_class.return_value = mock_session_service_instance

            # Call the RecommendationAgent constructor
            RecommendationAgent()

            # Assert that google.adk.Agent was called
            mock_agent_class.assert_called_once()
            call_args = mock_agent_class.call_args

            # Verify the arguments passed to google.adk.Agent
            assert "model" in call_args.kwargs
            assert call_args.kwargs["model"] == "gemini-2.0-flash-exp"
            assert call_args.kwargs["name"] == "konnect_recommendation_agent"
            assert "instruction" in call_args.kwargs
            assert "tools" in call_args.kwargs
            assert len(call_args.kwargs["tools"]) == 4


class TestAgentFactory:
    """Test the agent factory function."""

    @patch("konnect.agents.recommendation.RecommendationAgent")
    def test_create_recommendation_agent_default(self, mock_agent_class):
        """Test creating agent with default parameters."""
        mock_agent_instance = Mock()
        mock_agent_class.return_value = mock_agent_instance

        agent = create_recommendation_agent()

        mock_agent_class.assert_called_once_with(model="gemini-2.0-flash-exp")
        assert agent == mock_agent_instance

    @patch("konnect.agents.recommendation.RecommendationAgent")
    def test_create_recommendation_agent_custom_model(self, mock_agent_class):
        """Test creating agent with custom model."""
        mock_agent_instance = Mock()
        mock_agent_class.return_value = mock_agent_instance

        custom_model = "gemini-1.5-pro"
        agent = create_recommendation_agent(model=custom_model)

        mock_agent_class.assert_called_once_with(model=custom_model)
        assert agent == mock_agent_instance


class TestAgentIntegration:
    """Integration tests for the agents (without mocking ADK)."""

    def test_agent_tools_integration(self):
        """Test that agent tools work correctly together."""
        # Test that tools return consistent data
        popular = get_popular_items()
        electronics = search_items_by_category("Electronics")
        budget_items = get_price_range_items(0, 1000)

        # All should return lists
        assert isinstance(popular, list)
        assert isinstance(electronics, list)
        assert isinstance(budget_items, list)

        # Should have some overlap in electronics items
        popular_electronics = [
            item for item in popular if item["category"] == "Electronics"
        ]
        assert len(popular_electronics) > 0

        # Budget items should include popular items within range
        budget_popular = [item for item in popular if item["price"] <= 1000]
        for item in budget_popular:
            assert item in budget_items or any(
                bi["title"] == item["title"] for bi in budget_items
            )

    @pytest.mark.skip(reason="Requires Google API credentials")
    def test_real_agent_initialization(self):
        """Test real agent initialization (requires credentials)."""
        # This test is skipped by default as it requires real API credentials
        # Uncomment when testing with real credentials
        agent = RecommendationAgent()
        assert agent.agent is not None
