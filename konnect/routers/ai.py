"""AI router for recommendations, seller insights, and advanced AI features"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_current_active_user
from ..schemas import (
    AIRecommendationsResponse,
    SellerInsights,
    AISearchRequest,
    AISearchResponse,
    PriceSuggestionRequest,
    PriceSuggestionResponse,
    DescriptionGenerationRequest,
    DescriptionGenerationResponse,
)
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/recommendations", response_model=AIRecommendationsResponse)
async def get_ai_recommendations(
    current_user: dict = Depends(get_current_active_user),
    limit: int = 10,
):
    """Get AI-powered personalized recommendations"""
    if not supabase:
        raise HTTPException(
            status_code=503, detail="AI recommendation service not available"
        )

    try:
        # Get recent listings as recommendations (simplified approach)
        response = (
            supabase.table("listings")
            .select("*")
            .eq("is_active", True)
            .neq("user_id", current_user["id"])  # Don't recommend own listings
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        recommendations = []
        for item in response.data or []:
            recommendation = {
                "listing_id": item["id"],
                "title": item["title"],
                "price": item["price"],
                "category": item["category"],
                "confidence_score": 0.8,  # Mock confidence score
                "reason": "Based on recent activity and popular items",
            }
            recommendations.append(recommendation)

        return AIRecommendationsResponse(
            user_id=current_user["id"],
            recommendations=recommendations,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error generating AI recommendations: {e}")
        raise HTTPException(
            status_code=503, detail="AI recommendation service temporarily unavailable"
        )


@router.get("/seller-insights", response_model=SellerInsights)
async def get_seller_insights(
    current_user: dict = Depends(get_current_active_user),
):
    """Get AI-powered seller insights and analytics"""
    if not supabase:
        raise HTTPException(
            status_code=503, detail="Seller insights service not available"
        )

    # Verify user is a seller
    if current_user.get("role") != "seller":
        raise HTTPException(
            status_code=403, detail="Only verified sellers can access seller insights"
        )

    try:
        # Get seller's listings
        listings_response = (
            supabase.table("listings")
            .select("*")
            .eq("user_id", current_user["id"])
            .eq("is_active", True)
            .execute()
        )

        # Get seller's orders
        orders_response = (
            supabase.table("orders")
            .select("*")
            .eq("seller_id", current_user["id"])
            .execute()
        )

        listings = listings_response.data or []
        orders = orders_response.data or []

        # Calculate basic stats
        total_sales = len(orders)
        total_revenue = sum(order["total_amount"] for order in orders)
        avg_order_value = total_revenue / total_sales if total_sales > 0 else 0

        # Get top products (most orders)
        product_counts = {}
        for order in orders:
            listing_id = order["listing_id"]
            product_counts[listing_id] = product_counts.get(listing_id, 0) + 1

        top_products = []
        for listing_id, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            listing = next((l for l in listings if l["id"] == listing_id), None)
            if listing:
                top_products.append({
                    "listing_id": listing_id,
                    "title": listing["title"],
                    "orders": count,
                    "revenue": sum(o["total_amount"] for o in orders if o["listing_id"] == listing_id)
                })

        insights = SellerInsights(
            seller_id=current_user["id"],
            total_sales=total_sales,
            total_revenue=total_revenue,
            average_order_value=avg_order_value,
            top_products=top_products,
            sales_trend=[],  # Would be populated with trend analysis
            customer_satisfaction=0.0,  # Would be calculated from reviews/ratings
            recommendations=[
                "Consider offering bundle deals to increase average order value",
                "Focus on your top-performing product categories",
                "Consider offering faster shipping options",
            ],
        )

        return insights

    except Exception as e:
        logger.error(f"Error generating seller insights: {e}")
        raise HTTPException(
            status_code=503, detail="Seller insights service temporarily unavailable"
        )


@router.get("/market-analysis")
async def get_market_analysis(
    current_user: dict = Depends(get_current_active_user),
):
    """Get AI-powered market analysis and trends"""
    if not supabase:
        raise HTTPException(
            status_code=503, detail="Market analysis service not available"
        )

    try:
        # Get basic market data
        listings_response = (
            supabase.table("listings")
            .select("category, price, created_at")
            .eq("is_active", True)
            .execute()
        )

        listings = listings_response.data or []
        
        # Simple analysis
        categories = {}
        for listing in listings:
            category = listing["category"]
            if category not in categories:
                categories[category] = {"count": 0, "total_price": 0, "prices": []}
            categories[category]["count"] += 1
            categories[category]["total_price"] += listing["price"]
            categories[category]["prices"].append(listing["price"])

        # Calculate average prices
        for category in categories:
            prices = categories[category]["prices"]
            categories[category]["avg_price"] = sum(prices) / len(prices) if prices else 0
            categories[category]["min_price"] = min(prices) if prices else 0
            categories[category]["max_price"] = max(prices) if prices else 0

        return {
            "message": "Market analysis completed",
            "total_listings": len(listings),
            "categories": categories,
            "features": [
                "Price trend analysis",
                "Demand forecasting", 
                "Competitive analysis",
                "Seasonal trends",
            ],
        }

    except Exception as e:
        logger.error(f"Error generating market analysis: {e}")
        raise HTTPException(
            status_code=503, detail="Market analysis service temporarily unavailable"
        )


# AI-Powered Semantic Search
@router.post("/search", response_model=AISearchResponse)
async def ai_semantic_search(
    search_request: AISearchRequest,
    current_user: dict = Depends(get_current_active_user),
):
    """AI-powered semantic search with natural language queries"""
    if not supabase:
        raise HTTPException(
            status_code=503, detail="AI search service not available"
        )

    try:
        # Simple text-based search using Supabase
        response = (
            supabase.table("listings")
            .select("*")
            .eq("is_active", True)
            .or_(f"title.ilike.%{search_request.query}%,description.ilike.%{search_request.query}%")
            .limit(search_request.max_results)
            .execute()
        )

        results = []
        for item in response.data or []:
            result = {
                "listing_id": item["id"],
                "title": item["title"],
                "description": item["description"],
                "price": item["price"],
                "category": item["category"],
                "seller_username": "Unknown",  # Would be populated with join
                "marketplace_name": "Unknown",  # Would be populated with join
                "relevance_score": 0.8,  # Mock relevance score
                "explanation": f"Found based on text match for '{search_request.query}'",
                "matched_keywords": [search_request.query],
            }
            results.append(result)

        return AISearchResponse(
            query=search_request.query,
            results=results,
            total_found=len(results),
            search_time_ms=100,  # Mock search time
            explanation=f"Found {len(results)} results for '{search_request.query}'",
        )

    except Exception as e:
        logger.error(f"Error in AI semantic search: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI search service temporarily unavailable: {str(e)}",
        )


# AI Price Suggestion
@router.post("/suggest-price", response_model=PriceSuggestionResponse)
async def ai_price_suggestion(
    price_request: PriceSuggestionRequest,
    current_user: dict = Depends(get_current_active_user),
):
    """AI-powered price suggestion for sellers"""
    if not supabase:
        raise HTTPException(
            status_code=503, detail="AI price suggestion service not available"
        )

    try:
        # Get similar listings for price analysis
        response = (
            supabase.table("listings")
            .select("*")
            .eq("is_active", True)
            .eq("category", price_request.category)
            .execute()
        )

        similar_listings = response.data or []
        
        if similar_listings:
            prices = [listing["price"] for listing in similar_listings]
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            # Simple price suggestion logic
            suggested_min = avg_price * 0.8
            suggested_max = avg_price * 1.2
            suggested_recommended = avg_price
        else:
            # Default suggestions if no similar listings
            suggested_min = 50.0
            suggested_max = 200.0
            suggested_recommended = 100.0
            avg_price = 100.0
            min_price = 50.0
            max_price = 200.0

        return PriceSuggestionResponse(
            suggested_price_range={
                "min": suggested_min,
                "max": suggested_max,
                "recommended": suggested_recommended
            },
            market_analysis={
                "average_price": avg_price,
                "price_trend": "stable",
                "competition_level": "medium",
            },
            reasoning=f"Based on {len(similar_listings)} similar listings in {price_request.category} category",
            similar_listings=similar_listings[:5],  # Top 5 similar listings
            confidence_score=0.7,
        )

    except Exception as e:
        logger.error(f"Error in AI price suggestion: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI price suggestion service temporarily unavailable: {str(e)}",
        )


# AI Description Generation
@router.post("/generate-description", response_model=DescriptionGenerationResponse)
async def ai_generate_description(
    description_request: DescriptionGenerationRequest,
    current_user: dict = Depends(get_current_active_user),
):
    """AI-powered description generation for sellers"""
    if not supabase:
        raise HTTPException(
            status_code=503, detail="AI description generation service not available"
        )

    try:
        # Simple description generation based on input
        base_description = f"{description_request.title}"
        
        if description_request.condition:
            base_description += f" in {description_request.condition} condition"
        
        if description_request.brand:
            base_description += f" by {description_request.brand}"
        
        if description_request.key_features:
            features_text = ", ".join(description_request.key_features)
            base_description += f". Key features include: {features_text}"
        
        # Add category-specific details
        if description_request.category:
            base_description += f". Perfect for students looking for {description_request.category.lower()}."
        
        # Generate alternative descriptions
        alternatives = [
            f"Great {description_request.title} for students",
            f"Quality {description_request.title} at an affordable price",
            f"Student-friendly {description_request.title} in excellent condition"
        ]

        # Generate keywords
        keywords = [description_request.title.lower()]
        if description_request.category:
            keywords.append(description_request.category.lower())
        if description_request.brand:
            keywords.append(description_request.brand.lower())
        keywords.extend(["student", "affordable", "quality"])

        return DescriptionGenerationResponse(
            generated_description=base_description,
            alternative_descriptions=alternatives,
            suggested_keywords=keywords,
            seo_score=0.8,  # Mock SEO score
            readability_score=0.9,  # Mock readability score
        )

    except Exception as e:
        logger.error(f"Error in AI description generation: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI description generation service temporarily unavailable: {str(e)}",
        )
