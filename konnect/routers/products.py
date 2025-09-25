"""Products router for advanced product search and filtering"""

import logging
from fastapi import APIRouter, Query, HTTPException

from ..schemas import ProductSearchFilters, ProductSearchResponse, ProductSearchResult
from ..supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search", response_model=ProductSearchResponse)
async def search_products(
    # Query parameters
    query: str = Query(None, description="Search query for product title/description"),
    category: str = Query(None, description="Filter by product category"),
    min_price: float = Query(None, ge=0, description="Minimum price filter"),
    max_price: float = Query(None, ge=0, description="Maximum price filter"),
    marketplace_id: int = Query(None, description="Filter by marketplace ID"),
    verified_sellers_only: bool = Query(
        False, description="Show only verified seller products"
    ),
    sort_by: str = Query(
        "relevance",
        description="Sort by: relevance, price_asc, price_desc, newest, oldest",
    ),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Advanced product search with filtering and sorting"""
    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Product search service not available",
        )

    try:
        # Build filters object
        filters = ProductSearchFilters(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            marketplace_id=marketplace_id,
            verified_sellers_only=verified_sellers_only,
            sort_by=sort_by,
        )

        # Calculate offset
        offset = (page - 1) * page_size

        # Build Supabase query
        query_builder = supabase.table("listings").select("*").eq("is_active", True)

        # Apply filters
        if category:
            query_builder = query_builder.eq("category", category)
        if marketplace_id:
            query_builder = query_builder.eq("marketplace_id", marketplace_id)
        if min_price is not None:
            query_builder = query_builder.gte("price", min_price)
        if max_price is not None:
            query_builder = query_builder.lte("price", max_price)
        if verified_sellers_only:
            query_builder = query_builder.eq("profiles.is_verified_seller", True)

        # Apply text search if query provided
        if query:
            query_builder = query_builder.or_(
                f"title.ilike.%{query}%,description.ilike.%{query}%"
            )

        # Apply sorting
        if sort_by == "price_asc":
            query_builder = query_builder.order("price", desc=False)
        elif sort_by == "price_desc":
            query_builder = query_builder.order("price", desc=True)
        elif sort_by == "newest":
            query_builder = query_builder.order("created_at", desc=True)
        elif sort_by == "oldest":
            query_builder = query_builder.order("created_at", desc=False)
        else:  # relevance or default
            query_builder = query_builder.order("created_at", desc=True)

        # Apply pagination
        query_builder = query_builder.range(offset, offset + page_size - 1)

        # Execute query
        response = query_builder.execute()

        # Transform results to match schema
        results = []
        for item in response.data or []:
            result = ProductSearchResult(
                id=item["id"],
                title=item["title"],
                description=item["description"],
                price=item["price"],
                category=item["category"],
                marketplace_id=item["marketplace_id"],
                marketplace_name="Unknown",  # Will be populated separately if needed
                seller_id=item["user_id"],
                seller_username="Unknown",  # Will be populated separately if needed
                seller_verified=False,  # Will be populated separately if needed
                created_at=item["created_at"],
            )
            results.append(result)

        # Get total count for pagination
        count_query = (
            supabase.table("listings").select("id", count="exact").eq("is_active", True)
        )

        if category:
            count_query = count_query.eq("category", category)
        if marketplace_id:
            count_query = count_query.eq("marketplace_id", marketplace_id)
        if min_price is not None:
            count_query = count_query.gte("price", min_price)
        if max_price is not None:
            count_query = count_query.lte("price", max_price)
        if query:
            count_query = count_query.or_(
                f"title.ilike.%{query}%,description.ilike.%{query}%"
            )

        count_response = count_query.execute()
        total_count = count_response.count if count_response.count else 0

        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size

        return ProductSearchResponse(
            results=results,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            filters_applied=filters,
        )

    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search products: {str(e)}",
        )


@router.get("/categories")
async def get_product_categories():
    """Get all available product categories"""
    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Product categories service not available",
        )

    try:
        # Get distinct categories from listings
        response = (
            supabase.table("listings")
            .select("category")
            .eq("is_active", True)
            .not_.is_("category", "null")
            .execute()
        )

        # Extract unique categories
        categories = list(
            set([item["category"] for item in response.data if item["category"]])
        )
        categories.sort()  # Sort alphabetically

        return {"categories": categories}

    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {str(e)}",
        )


@router.get("/trending")
async def get_trending_products(
    limit: int = Query(
        10, ge=1, le=50, description="Number of trending products to return"
    ),
):
    """Get trending/popular products"""
    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Trending products service not available",
        )

    try:
        # Get recent listings as trending (in a real app, this would be based on views, purchases, etc.)
        response = (
            supabase.table("listings")
            .select(
                "*, profiles!listings_user_id_fkey(username), marketplaces!listings_marketplace_id_fkey(name)"
            )
            .eq("is_active", True)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        trending_products = response.data or []

        return {"trending_products": trending_products}

    except Exception as e:
        logger.error(f"Error fetching trending products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch trending products: {str(e)}",
        )


@router.get("/recommendations/{product_id}")
async def get_related_products(
    product_id: int,
    limit: int = Query(
        5, ge=1, le=20, description="Number of recommendations to return"
    ),
):
    """Get products related to a specific product"""
    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Product recommendations service not available",
        )

    try:
        # Verify product exists
        product_response = (
            supabase.table("listings")
            .select("*")
            .eq("id", product_id)
            .eq("is_active", True)
            .single()
            .execute()
        )

        if not product_response.data:
            raise HTTPException(status_code=404, detail="Product not found")

        product = product_response.data

        # Find related products by category and similar price range
        price_range = product["price"] * 0.5  # 50% price range
        min_price = product["price"] - price_range
        max_price = product["price"] + price_range

        response = (
            supabase.table("listings")
            .select(
                "*, profiles!listings_user_id_fkey(username), marketplaces!listings_marketplace_id_fkey(name)"
            )
            .eq("is_active", True)
            .neq("id", product_id)  # Exclude the current product
            .eq("category", product["category"])  # Same category
            .gte("price", min_price)
            .lte("price", max_price)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        related_products = response.data or []

        return {"related_products": related_products}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching related products for {product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch related products: {str(e)}",
        )
