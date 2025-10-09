#!/usr/bin/env python3
"""
Celery worker script for running background recommendation tasks

Usage:
    python celery_worker.py worker --loglevel=info
    python celery_worker.py beat --loglevel=info  # For scheduler

This would normally be run as:
    celery -A konnect.tasks worker --loglevel=info
    celery -A konnect.tasks beat --loglevel=info
"""

import os
import sys

# Add the konnect package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    # Simple worker runner for demonstration
    # In production, you'd use the celery CLI command

    print("Starting Celery worker for Konnect recommendations...")
    print("Available tasks:")
    print("  - generate_recommendations_for_user")
    print("  - generate_recommendations_for_active_users")
    print("")
    print("Scheduled tasks:")
    print("  - generate_recommendations_for_active_users: every hour")
    print("")
    print("Note: In production, run with:")
    print("  celery -A konnect.tasks worker --loglevel=info")
    print("  celery -A konnect.tasks beat --loglevel=info")

    # For demonstration purposes, manually trigger some tasks
    print("\nDemonstrating task execution...")

    from konnect.tasks import (
        generate_recommendations_for_active_users,
        generate_recommendations_for_user,
    )

    # Simulate running individual user task
    print("Running task: generate_recommendations_for_user(user_id=1)")
    result = generate_recommendations_for_user(1)
    print(f"Result: {result}")

    # Simulate running batch task
    print("Running task: generate_recommendations_for_active_users()")
    result = generate_recommendations_for_active_users()
    print(f"Result: {result}")
