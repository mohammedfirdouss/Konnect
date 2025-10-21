"""Gamification router for points, badges, and leaderboards"""

import logging
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_current_active_user
from ..schemas import (
    UserPoints,
    UserBadge,
    PointsTransaction,
    LeaderboardResponse,
    LeaderboardEntry,
)
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gamification", tags=["gamification"])

# Points system configuration
POINTS_CONFIG = {
    "purchase_completed": 50,
    "sale_completed": 100,
    "review_given": 25,
    "review_received": 15,
    "listing_created": 10,
    "first_sale": 200,
    "level_5": 500,
    "level_10": 1000,
    "badge_earned": 50,
}

# Level thresholds (points required for each level)
LEVEL_THRESHOLDS = [
    0, 100, 250, 500, 1000, 2000, 3500, 5500, 8000, 11000, 15000
]


def calculate_level(points: int) -> int:
    """Calculate user level based on points"""
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if points < threshold:
            return i
    return len(LEVEL_THRESHOLDS)


def award_points(
    user_id: int,
    points: int,
    transaction_type: str,
    description: str = None,
    related_entity_id: int = None,
    related_entity_type: str = None,
) -> bool:
    """Award points to a user and create transaction record"""
    if not supabase:
        logger.error("Supabase not available for points awarding")
        return False

    try:
        # Get current user points
        points_response = (
            supabase.table("user_points")
            .select("*")
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if points_response.data:
            # Update existing points
            current_points = points_response.data["points"]
            new_points = current_points + points
            new_level = calculate_level(new_points)
            
            update_response = (
                supabase.table("user_points")
                .update({
                    "points": new_points,
                    "level": new_level,
                    "total_points_earned": points_response.data["total_points_earned"] + points,
                    "updated_at": datetime.utcnow().isoformat()
                })
                .eq("user_id", user_id)
                .execute()
            )
        else:
            # Create new points record
            new_points = points
            new_level = calculate_level(points)
            
            insert_response = (
                supabase.table("user_points")
                .insert({
                    "user_id": user_id,
                    "points": new_points,
                    "level": new_level,
                    "total_points_earned": points,
                })
                .execute()
            )

        # Create transaction record
        transaction_response = (
            supabase.table("points_transactions")
            .insert({
                "user_id": user_id,
                "points_change": points,
                "transaction_type": transaction_type,
                "description": description,
                "related_entity_id": related_entity_id,
                "related_entity_type": related_entity_type,
            })
            .execute()
        )

        # Check for level up badges
        if new_level > 1:
            check_level_badges(user_id, new_level)

        logger.info(f"Awarded {points} points to user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error awarding points: {e}")
        return False


def check_level_badges(user_id: int, level: int):
    """Check and award level-based badges"""
    badge_name = f"Level {level} Achiever"
    badge_description = f"Reached level {level} in the campus marketplace"
    
    # Check if user already has this badge
    existing_badge = (
        supabase.table("user_badges")
        .select("*")
        .eq("user_id", user_id)
        .eq("badge_name", badge_name)
        .execute()
    )
    
    if not existing_badge.data:
        # Award the badge
        badge_response = (
            supabase.table("user_badges")
            .insert({
                "user_id": user_id,
                "badge_name": badge_name,
                "badge_description": badge_description,
                "badge_type": "milestone",
                "points_awarded": POINTS_CONFIG.get("badge_earned", 50),
            })
            .execute()
        )
        
        if badge_response.data:
            # Award points for earning the badge
            award_points(
                user_id,
                POINTS_CONFIG.get("badge_earned", 50),
                "badge_earned",
                f"Earned {badge_name} badge",
                badge_response.data[0]["id"],
                "badge"
            )


def update_leaderboard(marketplace_id: int):
    """Update campus leaderboard for a marketplace"""
    if not supabase:
        return

    try:
        # Get all users with points for this marketplace
        users_response = (
            supabase.table("user_points")
            .select("*, users!user_points_user_id_fkey(username, full_name)")
            .execute()
        )

        if not users_response.data:
            return

        # Sort by points descending
        sorted_users = sorted(
            users_response.data,
            key=lambda x: x["points"],
            reverse=True
        )

        # Update leaderboard
        for rank, user_data in enumerate(sorted_users, 1):
            user_id = user_data["user_id"]
            points = user_data["points"]
            level = user_data["level"]
            
            # Count badges for this user
            badges_response = (
                supabase.table("user_badges")
                .select("id")
                .eq("user_id", user_id)
                .execute()
            )
            badges_count = len(badges_response.data) if badges_response.data else 0

            # Upsert leaderboard entry
            leaderboard_response = (
                supabase.table("campus_leaderboard")
                .upsert({
                    "marketplace_id": marketplace_id,
                    "user_id": user_id,
                    "rank": rank,
                    "points": points,
                    "level": level,
                    "badges_count": badges_count,
                    "updated_at": datetime.utcnow().isoformat()
                })
                .execute()
            )

        logger.info(f"Updated leaderboard for marketplace {marketplace_id}")

    except Exception as e:
        logger.error(f"Error updating leaderboard: {e}")


@router.get("/points", response_model=UserPoints)
async def get_user_points(
    current_user: dict = Depends(get_current_active_user),
):
    """Get current user's points and level"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification service not available",
        )

    try:
        response = (
            supabase.table("user_points")
            .select("*")
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        if response.data:
            return response.data
        else:
            # Create initial points record
            create_response = (
                supabase.table("user_points")
                .insert({
                    "user_id": current_user["id"],
                    "points": 0,
                    "level": 1,
                    "total_points_earned": 0,
                })
                .execute()
            )
            return create_response.data[0]

    except Exception as e:
        logger.error(f"Error fetching user points: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user points",
        )


@router.get("/ai-recommendations")
async def get_ai_gamification_recommendations(
    current_user: dict = Depends(get_current_active_user),
):
    """Get AI-powered gamification recommendations"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification service not available",
        )

    try:
        # Get user's gamification data
        points_response = (
            supabase.table("user_points")
            .select("*")
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        badges_response = (
            supabase.table("user_badges")
            .select("*")
            .eq("user_id", current_user["id"])
            .execute()
        )

        transactions_response = (
            supabase.table("points_transactions")
            .select("*")
            .eq("user_id", current_user["id"])
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )

        # Get user's activity data
        orders_response = (
            supabase.table("orders")
            .select("*")
            .eq("buyer_id", current_user["id"])
            .execute()
        )

        listings_response = (
            supabase.table("listings")
            .select("*")
            .eq("user_id", current_user["id"])
            .execute()
        )

        # Prepare data for AI analysis
        user_level = points_response.data.get("level", 1) if points_response.data else 1
        user_points = points_response.data.get("points", 0) if points_response.data else 0
        badges_count = len(badges_response.data) if badges_response.data else 0
        transactions = transactions_response.data or []
        orders = orders_response.data or []
        listings = listings_response.data or []

        # Calculate activity metrics
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o["status"] == "completed"])
        total_listings = len(listings)
        active_listings = len([l for l in listings if l["is_active"]])

        # Generate AI recommendations
        try:
            from ..routers.ai import generate_ai_response, AI_SERVICE_ENABLED
            
            if AI_SERVICE_ENABLED:
                context = f"""
                User Gamification Profile:
                - Current Level: {user_level}
                - Current Points: {user_points}
                - Badges Earned: {badges_count}
                - Total Orders: {total_orders}
                - Completed Orders: {completed_orders}
                - Total Listings: {total_listings}
                - Active Listings: {active_listings}
                
                Recent Activity: {len(transactions)} point transactions
                
                Provide personalized gamification recommendations to help this user level up and earn more badges.
                """
                
                ai_recommendations = generate_ai_response(
                    "Analyze this user's gamification profile and provide actionable recommendations:",
                    context
                )
            else:
                ai_recommendations = "AI service not available for personalized recommendations"
        except Exception as e:
            logger.warning(f"AI gamification recommendations failed: {e}")
            ai_recommendations = "AI service temporarily unavailable"

        # Calculate next level requirements
        next_level_threshold = LEVEL_THRESHOLDS[user_level] if user_level < len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1]
        points_to_next_level = next_level_threshold - user_points

        # Suggest specific actions based on current level
        suggested_actions = []
        if user_level < 5:
            suggested_actions.extend([
                "Complete your first sale to earn 100 points",
                "Create 5 active listings to earn listing points",
                "Leave reviews for completed orders"
            ])
        elif user_level < 10:
            suggested_actions.extend([
                "Aim for 10 completed sales this month",
                "Maintain 5+ active listings",
                "Help other users with marketplace questions"
            ])
        else:
            suggested_actions.extend([
                "Mentor new sellers to earn mentor badges",
                "Achieve 95%+ completion rate",
                "Participate in campus marketplace events"
            ])

        return {
            "user_id": current_user["id"],
            "current_level": user_level,
            "current_points": user_points,
            "badges_count": badges_count,
            "points_to_next_level": points_to_next_level,
            "next_level_threshold": next_level_threshold,
            "suggested_actions": suggested_actions,
            "ai_recommendations": ai_recommendations,
            "activity_summary": {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "total_listings": total_listings,
                "active_listings": active_listings,
                "recent_transactions": len(transactions)
            }
        }

    except Exception as e:
        logger.error(f"Error generating AI gamification recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate gamification recommendations",
        )


@router.get("/badges", response_model=List[UserBadge])
async def get_user_badges(
    current_user: dict = Depends(get_current_active_user),
):
    """Get current user's badges"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification service not available",
        )

    try:
        response = (
            supabase.table("user_badges")
            .select("*")
            .eq("user_id", current_user["id"])
            .order("earned_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:
        logger.error(f"Error fetching user badges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user badges",
        )


@router.get("/transactions", response_model=List[PointsTransaction])
async def get_points_transactions(
    current_user: dict = Depends(get_current_active_user),
    limit: int = 50,
):
    """Get current user's points transaction history"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification service not available",
        )

    try:
        response = (
            supabase.table("points_transactions")
            .select("*")
            .eq("user_id", current_user["id"])
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return response.data or []

    except Exception as e:
        logger.error(f"Error fetching points transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch points transactions",
        )


@router.get("/leaderboard/{marketplace_id}", response_model=LeaderboardResponse)
async def get_campus_leaderboard(
    marketplace_id: int,
    limit: int = 20,
):
    """Get campus leaderboard for a marketplace"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification service not available",
        )

    try:
        # Update leaderboard first
        update_leaderboard(marketplace_id)

        # Get leaderboard entries
        response = (
            supabase.table("campus_leaderboard")
            .select("*, users!campus_leaderboard_user_id_fkey(username, full_name)")
            .eq("marketplace_id", marketplace_id)
            .order("rank")
            .limit(limit)
            .execute()
        )

        entries = []
        for item in response.data or []:
            user_data = item.get("users", {})
            entry = LeaderboardEntry(
                rank=item["rank"],
                user_id=item["user_id"],
                username=user_data.get("username", "Unknown"),
                full_name=user_data.get("full_name"),
                points=item["points"],
                level=item["level"],
                badges_count=item["badges_count"],
            )
            entries.append(entry)

        return LeaderboardResponse(
            entries=entries,
            total_count=len(entries),
            marketplace_id=marketplace_id,
            updated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leaderboard",
        )


@router.post("/award-points")
async def award_points_to_user(
    user_id: int,
    points: int,
    transaction_type: str,
    description: str = None,
    current_user: dict = Depends(get_current_active_user),
):
    """Award points to a user (admin only)"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can award points",
        )

    success = award_points(
        user_id=user_id,
        points=points,
        transaction_type=transaction_type,
        description=description,
    )

    if success:
        return {"message": f"Successfully awarded {points} points to user {user_id}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to award points",
        )