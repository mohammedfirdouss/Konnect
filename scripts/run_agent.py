#!/usr/bin/env python3
"""
Agent Runner Script for Konnect

This script provides a command-line interface to interact with
Konnect's AI agents, particularly the recommendation agent.
"""

import argparse
import sys
import os
from typing import Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from konnect.agents import RecommendationAgent


def main():
    """Main entry point for the agent runner script."""
    parser = argparse.ArgumentParser(
        description="Run Konnect AI agents for recommendations and assistance"
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query to send to the recommendation agent"
    )

    parser.add_argument(
        "--category",
        help="Search for recommendations in a specific category"
    )

    parser.add_argument(
        "--budget",
        type=float,
        help="Maximum budget for recommendations"
    )

    parser.add_argument(
        "--min-price",
        type=float,
        help="Minimum price for budget-based search"
    )

    parser.add_argument(
        "--max-price",
        type=float,
        help="Maximum price for budget-based search"
    )

    parser.add_argument(
        "--model",
        default="gemini-2.0-flash-exp",
        help="Google GenAI model to use (default: gemini-2.0-flash-exp)"
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive mode for multiple queries"
    )

    args = parser.parse_args()

    # Create the recommendation agent
    try:
        print("🤖 Initializing Konnect Recommendation Agent...")
        agent = RecommendationAgent(model=args.model)
        print(f"✅ Agent initialized with model: {args.model}")
        print("-" * 60)
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return 1

    # Handle different modes of operation
    if args.interactive:
        return run_interactive_mode(agent)

    elif args.category:
        return run_category_search(agent, args.category, args.budget)

    elif args.min_price is not None and args.max_price is not None:
        return run_budget_search(agent, args.min_price, args.max_price)

    elif args.query:
        return run_single_query(agent, args.query)

    else:
        # No arguments provided, show examples
        show_examples()
        return 0


def run_single_query(agent: RecommendationAgent, query: str) -> int:
    """Run a single query against the agent."""
    print(f"📝 Query: {query}")
    print("-" * 60)

    try:
        response = agent.get_recommendations(query)
        print("🎯 Recommendations:")
        print(response)
        return 0
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")
        return 1


def run_category_search(agent: RecommendationAgent, category: str, budget: Optional[float]) -> int:
    """Run a category-based search."""
    budget_text = f" (Budget: ${budget})" if budget else ""
    print(f"📂 Category Search: {category}{budget_text}")
    print("-" * 60)

    try:
        response = agent.get_category_recommendations(category, budget)
        print("🎯 Category Recommendations:")
        print(response)
        return 0
    except Exception as e:
        print(f"❌ Error getting category recommendations: {e}")
        return 1


def run_budget_search(agent: RecommendationAgent, min_price: float, max_price: float) -> int:
    """Run a budget-based search."""
    print(f"💰 Budget Search: ${min_price} - ${max_price}")
    print("-" * 60)

    try:
        response = agent.get_budget_recommendations(min_price, max_price)
        print("🎯 Budget Recommendations:")
        print(response)
        return 0
    except Exception as e:
        print(f"❌ Error getting budget recommendations: {e}")
        return 1


def run_interactive_mode(agent: RecommendationAgent) -> int:
    """Run the agent in interactive mode."""
    print("🎪 Interactive Mode - Type 'quit' or 'exit' to stop")
    print("=" * 60)

    while True:
        try:
            query = input("\n💬 Enter your query: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not query:
                continue

            print("\n🤔 Thinking...")
            response = agent.get_recommendations(query)
            print("\n🎯 Recommendations:")
            print(response)
            print("-" * 40)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

    return 0


def show_examples():
    """Show usage examples."""
    print("🎯 Konnect Agent Runner - Usage Examples:")
    print("=" * 60)
    print()
    print("📝 Single Query:")
    print('  python scripts/run_agent.py "I need study materials for engineering"')
    print()
    print("📂 Category Search:")
    print("  python scripts/run_agent.py --category Electronics --budget 500")
    print()
    print("💰 Budget Search:")
    print("  python scripts/run_agent.py --min-price 20 --max-price 100")
    print()
    print("🎪 Interactive Mode:")
    print("  python scripts/run_agent.py --interactive")
    print()
    print("🔧 Custom Model:")
    print("  python scripts/run_agent.py --model gemini-1.5-pro \"Best laptops for students\"")
    print()


if __name__ == "__main__":
    sys.exit(main())
