"""AI router for recommendations, seller insights, and advanced AI features"""

import logging
import os
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

# AI Service Configuration
AI_SERVICE_ENABLED = False
AI_SERVICE_PROVIDER = None

# OpenAI Configuration
try:
    import openai

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        AI_SERVICE_ENABLED = True
        AI_SERVICE_PROVIDER = "openai"
        logger.info("OpenAI service configured successfully")
    else:
        logger.warning("OpenAI API key not found.")
except ImportError:
    logger.warning("OpenAI package not installed.")

# Google ADK Configuration
try:
    import google.generativeai as genai

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        if not AI_SERVICE_ENABLED:  # Use Google if OpenAI not available
            AI_SERVICE_ENABLED = True
            AI_SERVICE_PROVIDER = "google"
        logger.info("Google ADK service configured successfully")
    else:
        logger.warning("Google API key not found.")
except ImportError:
    logger.warning("Google ADK package not installed.")

# Check if any AI service is available
if not AI_SERVICE_ENABLED:
    logger.warning(
        "No AI service configured. Please set OPENAI_API_KEY or GOOGLE_API_KEY environment variables."
    )

router = APIRouter(prefix="/ai", tags=["ai"])


def generate_ai_response(prompt: str, context: str = "") -> str:
    """Generate AI response using available service (OpenAI or Google ADK)"""
    if not AI_SERVICE_ENABLED:
        return "AI service not available"

    try:
        if AI_SERVICE_PROVIDER == "openai":
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        elif AI_SERVICE_PROVIDER == "google":
            model = genai.GenerativeModel("gemini-pro")
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            response = model.generate_content(full_prompt)
            return response.text.strip()

    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return f"AI generation failed: {str(e)}"

    return "AI service not configured"


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

    if not AI_SERVICE_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Please set OPENAI_API_KEY or GOOGLE_API_KEY environment variable.",
        )

    try:
        # Get user's gamification data for better recommendations
        user_points_response = (
            supabase.table("user_points")
            .select("*")
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        user_level = 1
        user_points = 0
        if user_points_response.data:
            user_level = user_points_response.data.get("level", 1)
            user_points = user_points_response.data.get("points", 0)

        # Get user's purchase history for better recommendations
        purchase_response = (
            supabase.table("orders")
            .select("*, listings!orders_listing_id_fkey(*)")
            .eq("buyer_id", current_user["id"])
            .eq("status", "completed")
            .limit(10)
            .execute()
        )

        # Analyze user preferences based on purchase history
        preferred_categories = []
        avg_price_range = {"min": 0, "max": 1000}

        if purchase_response.data:
            categories = [
                order["listings"]["category"]
                for order in purchase_response.data
                if order.get("listings")
            ]
            preferred_categories = list(set(categories))

            prices = [
                order["listings"]["price"]
                for order in purchase_response.data
                if order.get("listings")
            ]
            if prices:
                avg_price_range = {
                    "min": max(0, min(prices) * 0.5),
                    "max": max(prices) * 1.5,
                }

        # Get listings that match user preferences
        query = (
            supabase.table("listings")
            .select("*")
            .eq("is_active", True)
            .neq("user_id", current_user["id"])
        )

        if preferred_categories:
            query = query.in_("category", preferred_categories)

        query = query.gte("price", avg_price_range["min"]).lte(
            "price", avg_price_range["max"]
        )

        response = query.order("created_at", desc=True).limit(limit * 2).execute()

        recommendations = []
        for item in response.data or []:
            # Calculate confidence score based on user level and preferences
            confidence_score = 0.6  # Base confidence

            if item["category"] in preferred_categories:
                confidence_score += 0.2

            if avg_price_range["min"] <= item["price"] <= avg_price_range["max"]:
                confidence_score += 0.1

            if user_level >= 5:  # Higher level users get better recommendations
                confidence_score += 0.1

            recommendation = {
                "listing_id": item["id"],
                "title": item["title"],
                "price": item["price"],
                "category": item["category"],
                "confidence_score": min(confidence_score, 1.0),
                "reason": (
                    f"Recommended based on your level {user_level}, "
                    f"{user_points} points, and preferences"
                ),
            }
            recommendations.append(recommendation)

        # Sort by confidence score and limit results
        recommendations.sort(key=lambda x: x["confidence_score"], reverse=True)
        recommendations = recommendations[:limit]

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

        # Get seller's gamification data
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

        # Get seller's reviews
        reviews_response = (
            supabase.table("user_reviews")
            .select("*")
            .eq("seller_id", current_user["id"])
            .execute()
        )

        reviews = reviews_response.data or []

        # Calculate basic stats
        total_sales = len(orders)
        total_revenue = sum(order["total_amount"] for order in orders)
        avg_order_value = total_revenue / total_sales if total_sales > 0 else 0

        # Gamification insights
        user_level = points_response.data.get("level", 1) if points_response.data else 1
        user_points = (
            points_response.data.get("points", 0) if points_response.data else 0
        )
        badges_count = len(badges_response.data) if badges_response.data else 0

        # Review insights
        avg_rating = (
            sum([r["rating"] for r in reviews]) / len(reviews) if reviews else 0
        )
        total_reviews = len(reviews)

        # Get top products (most orders)
        product_counts = {}
        for order in orders:
            listing_id = order["listing_id"]
            product_counts[listing_id] = product_counts.get(listing_id, 0) + 1

        top_products = []
        for listing_id, count in sorted(
            product_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]:
            listing = next(
                (item for item in listings if item["id"] == listing_id), None
            )
            if listing:
                top_products.append(
                    {
                        "listing_id": listing_id,
                        "title": listing["title"],
                        "orders": count,
                        "revenue": sum(
                            o["total_amount"]
                            for o in orders
                            if o["listing_id"] == listing_id
                        ),
                    }
                )

        # Generate AI-powered insights with gamification context
        if AI_SERVICE_ENABLED:
            context = f"""
            Seller Analytics:
            - Total Sales: {total_sales}
            - Total Revenue: ${total_revenue:.2f}
            - Average Order Value: ${avg_order_value:.2f}
            - User Level: {user_level}
            - User Points: {user_points}
            - Badges Earned: {badges_count}
            - Average Rating: {avg_rating:.1f}/5.0
            - Total Reviews: {total_reviews}
            
            Provide insights and recommendations for improving seller performance, including gamification strategies.
            """

            ai_recommendation_text = generate_ai_response(
                "Analyze this seller's performance and provide actionable insights including gamification recommendations:",
                context,
            )
        else:
            ai_recommendation_text = None

        recommendations = [
            f"Level {user_level} seller with {user_points} points - great progress!",
            f"Earned {badges_count} badges - consider targeting specific achievements",
            "Consider offering bundle deals to increase average order value",
            "Focus on your top-performing product categories",
            "Consider offering faster shipping options",
        ]

        if ai_recommendation_text:
            recommendations.insert(0, ai_recommendation_text)
        elif not AI_SERVICE_ENABLED:
            recommendations.append(
                "Enable AI services to unlock advanced seller insights"
            )

        insights = SellerInsights(
            seller_id=current_user["id"],
            total_sales=total_sales,
            total_revenue=total_revenue,
            average_order_value=avg_order_value,
            top_products=top_products,
            sales_trend=[],  # Would be populated with trend analysis
            customer_satisfaction=avg_rating,
            recommendations=recommendations,
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
            categories[category]["avg_price"] = (
                sum(prices) / len(prices) if prices else 0
            )
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
        raise HTTPException(status_code=503, detail="AI search service not available")

    if not AI_SERVICE_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Please set OPENAI_API_KEY or GOOGLE_API_KEY environment variable.",
        )

    try:
        # Get all listings for AI analysis
        all_listings_response = (
            supabase.table("listings")
            .select("*")
            .eq("is_active", True)
            .limit(100)  # Get more listings for AI to analyze
            .execute()
        )

        if not all_listings_response.data:
            return AISearchResponse(
                query=search_request.query,
                results=[],
                total_found=0,
                search_time_ms=0,
                explanation="No listings available for search",
            )

        # Use AI to find relevant listings
        listings_text = "\n".join(
            [
                f"ID: {item['id']}, Title: {item['title']}, Description: {item['description']}, Category: {item['category']}, Price: ${item['price']}"
                for item in all_listings_response.data
            ]
        )

        ai_prompt = f"""
        Given this user query: "{search_request.query}"
        
        And these available listings:
        {listings_text}
        
        Please identify the most relevant listings (IDs only) that match the user's intent. 
        Consider semantic meaning, not just exact word matches.
        Return only the IDs separated by commas, maximum {search_request.max_results} results.
        """

        ai_response = generate_ai_response(
            ai_prompt,
            "You are a helpful assistant that finds relevant products based on user queries.",
        )

        # Parse AI response to get relevant IDs
        try:
            relevant_ids = [
                int(id.strip()) for id in ai_response.split(",") if id.strip().isdigit()
            ]
        except (ValueError, AttributeError):
            relevant_ids = []

        # If AI didn't return valid IDs, fall back to text search
        if not relevant_ids:
            response = (
                supabase.table("listings")
                .select("*")
                .eq("is_active", True)
                .or_(
                    f"title.ilike.%{search_request.query}%,description.ilike.%{search_request.query}%"
                )
                .limit(search_request.max_results)
                .execute()
            )
        else:
            # Get listings by AI-selected IDs
            response = (
                supabase.table("listings")
                .select("*")
                .eq("is_active", True)
                .in_("id", relevant_ids)
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

            # Use AI for intelligent price analysis
            market_data = "\n".join(
                [
                    f"Title: {item['title']}, Price: ${item['price']}, Condition: {item.get('condition', 'unknown')}"
                    for item in similar_listings[:10]
                ]
            )

            ai_prompt = f"""
            Analyze the pricing for this product:
            Title: {price_request.title}
            Category: {price_request.category}
            Condition: {price_request.condition or "unknown"}
            Brand: {price_request.brand or "unknown"}
            
            Market data:
            {market_data}
            
            Please suggest:
            1. Minimum price (competitive)
            2. Maximum price (premium)
            3. Recommended price (optimal)
            4. Market trend (rising/stable/declining)
            5. Competition level (low/medium/high)
            
            Format: min_price|max_price|recommended_price|trend|competition
            """

            ai_response = generate_ai_response(
                ai_prompt, "You are a pricing expert for online marketplaces."
            )

            try:
                parts = ai_response.split("|")
                if len(parts) >= 5:
                    suggested_min = float(parts[0].strip())
                    suggested_max = float(parts[1].strip())
                    suggested_recommended = float(parts[2].strip())
                    price_trend = parts[3].strip().lower()
                    competition_level = parts[4].strip().lower()
                else:
                    raise ValueError("Invalid AI response format")
            except (ValueError, IndexError):
                # Fallback to simple calculation
                suggested_min = avg_price * 0.8
                suggested_max = avg_price * 1.2
                suggested_recommended = avg_price
                price_trend = "stable"
                competition_level = "medium"
        else:
            # Default suggestions if no similar listings
            suggested_min = 50.0
            suggested_max = 200.0
            suggested_recommended = 100.0
            avg_price = 100.0
            price_trend = "unknown"
            competition_level = "unknown"

        return PriceSuggestionResponse(
            suggested_price_range={
                "min": suggested_min,
                "max": suggested_max,
                "recommended": suggested_recommended,
            },
            market_analysis={
                "average_price": avg_price,
                "price_trend": price_trend,
                "competition_level": competition_level,
            },
            reasoning=f"AI-powered analysis based on {len(similar_listings)} similar listings in {price_request.category} category",
            similar_listings=similar_listings[:5],  # Top 5 similar listings
            confidence_score=0.8 if similar_listings else 0.5,
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
        # Use AI to generate compelling product descriptions
        product_info = f"""
        Product: {description_request.title}
        Category: {description_request.category or "General"}
        Condition: {description_request.condition or "Good"}
        Brand: {description_request.brand or "Unknown"}
        Key Features: {", ".join(description_request.key_features) if description_request.key_features else "Standard features"}
        """

        ai_prompt = f"""
        Create compelling product descriptions for a campus marketplace listing:
        
        {product_info}
        
        Please generate:
        1. A main description (2-3 sentences, engaging and student-friendly)
        2. Two alternative descriptions (different styles)
        3. SEO keywords (comma-separated)
        4. SEO score (0-1)
        5. Readability score (0-1)
        
        Format: main_description|alt1|alt2|keywords|seo_score|readability_score
        """

        ai_response = generate_ai_response(
            ai_prompt,
            "You are an expert copywriter specializing in student marketplace listings.",
        )

        try:
            parts = ai_response.split("|")
            if len(parts) >= 6:
                main_description = parts[0].strip()
                alt1 = parts[1].strip()
                alt2 = parts[2].strip()
                keywords_text = parts[3].strip()
                seo_score = float(parts[4].strip())
                readability_score = float(parts[5].strip())

                keywords = [k.strip() for k in keywords_text.split(",")]
                alternatives = [alt1, alt2]
            else:
                raise ValueError("Invalid AI response format")
        except (ValueError, IndexError):
            # Fallback to simple generation
            main_description = f"{description_request.title}"
            if description_request.condition:
                main_description += f" in {description_request.condition} condition"
            if description_request.brand:
                main_description += f" by {description_request.brand}"
            if description_request.key_features:
                features_text = ", ".join(description_request.key_features)
                main_description += f". Key features include: {features_text}"

            alternatives = [
                f"Great {description_request.title} for students",
                f"Quality {description_request.title} at an affordable price",
            ]

            keywords = [description_request.title.lower()]
            if description_request.category:
                keywords.append(description_request.category.lower())
            if description_request.brand:
                keywords.append(description_request.brand.lower())
            keywords.extend(["student", "affordable", "quality"])

            seo_score = 0.7
            readability_score = 0.8

        return DescriptionGenerationResponse(
            generated_description=main_description,
            alternative_descriptions=alternatives,
            suggested_keywords=keywords,
            seo_score=seo_score,
            readability_score=readability_score,
        )

    except Exception as e:
        logger.error(f"Error in AI description generation: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI description generation service temporarily unavailable: {str(e)}",
        )
