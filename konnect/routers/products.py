"""Products router for advanced product search and filtering"""


from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import ProductSearchFilters, ProductSearchResponse

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
    db: Session = Depends(get_db),
):
    """Advanced product search with filtering and sorting"""
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

    # Perform search
    search_results = crud.search_products(
        db, filters=filters, offset=offset, limit=page_size
    )

    # Calculate total pages
    total_pages = (search_results["total_count"] + page_size - 1) // page_size

    return ProductSearchResponse(
        results=search_results["results"],
        total_count=search_results["total_count"],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        filters_applied=filters,
    )


@router.get("/categories")
async def get_product_categories(db: Session = Depends(get_db)):
    """Get all available product categories"""
    categories = crud.get_all_categories(db)
    return {"categories": categories}


@router.get("/trending")
async def get_trending_products(
    limit: int = Query(
        10, ge=1, le=50, description="Number of trending products to return"
    ),
    db: Session = Depends(get_db),
):
    """Get trending/popular products"""
    # This could be based on recent views, purchases, or other engagement metrics
    trending = crud.get_trending_products(db, limit=limit)
    return {"trending_products": trending}


@router.get("/recommendations/{product_id}")
async def get_related_products(
    product_id: int,
    limit: int = Query(
        5, ge=1, le=20, description="Number of recommendations to return"
    ),
    db: Session = Depends(get_db),
):
    """Get products related to a specific product"""
    # Verify product exists
    product = crud.get_listing(db, product_id)
    if not product:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Product not found")

    # Find related products by category, price range, etc.
    related = crud.get_related_products(db, product_id, limit=limit)
    return {"related_products": related}
