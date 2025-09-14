"""
Main application module for Konnect
"""

from fastapi import FastAPI

from .database import create_tables
from .routers import auth, users, listings, agent

app = FastAPI(
    title="Konnect", description="Campus Tools with SolanaPay", version="0.1.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(agent.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Konnect - Campus Tools with SolanaPay"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "konnect"}


def add_numbers(a: int, b: int) -> int:
    """Simple function to add two numbers for testing purposes"""
    return a + b


def validate_payment_amount(amount: float) -> bool:
    """Validate payment amount for Solana transactions"""
    if amount <= 0:
        return False
    if amount > 1000000:  # Max amount limit
        return False
    return True
