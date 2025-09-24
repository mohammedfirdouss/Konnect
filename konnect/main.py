"""
Main application module for Konnect
"""

import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import metrics, trace
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pythonjsonlogger import jsonlogger

from .supabase_client import check_supabase_connection
from .routers import (
    admin,
    ai,
    auth,
    listings,
    marketplaces,
    orders,
    products,
    users,
)

# Configure OpenTelemetry Metrics
prometheus_reader = PrometheusMetricReader()
metrics.set_meter_provider(MeterProvider(metric_readers=[prometheus_reader]))

# Configure OpenTelemetry Tracing
trace.set_tracer_provider(TracerProvider())


# Configure structured JSON logging
def setup_logging():
    """Setup structured JSON logging"""
    logger = logging.getLogger()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create JSON formatter
    json_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    json_handler.setFormatter(formatter)
    logger.addHandler(json_handler)

    return logger


# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application on startup"""
    logger.info("Starting up Konnect application")
    try:
        # Check Supabase connection
        connection_status = check_supabase_connection()
        logger.info(f"Supabase connection status: {connection_status}")
        
        if not connection_status["supabase_configured"]:
            logger.warning("Supabase not properly configured - some features may not work")
        else:
            logger.info("Supabase connection verified successfully")
            
    except Exception as e:
        logger.error(f"Failed to verify Supabase connection: {e}")
        logger.warning("Continuing startup - some features may not work")
    yield
    logger.info("Shutting down Konnect application")


app = FastAPI(
    title="Konnect",
    description="Campus Tools with SolanaPay",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(marketplaces.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(ai.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint requested")
    return {"message": "Welcome to Konnect - Campus Tools with SolanaPay"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    
    # Check Supabase connection
    supabase_status = check_supabase_connection()
    
    health_status = {
        "status": "healthy" if supabase_status["supabase_configured"] else "degraded",
        "service": "konnect",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "supabase": supabase_status,
        "database": {
            "type": "supabase_postgresql",
            "connected": supabase_status["connection_test"] == "success" if "connection_test" in supabase_status else False
        }
    }
    
    return health_status


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    logger.info("Metrics endpoint requested")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/config")
async def get_config():
    """Get application configuration (non-sensitive)"""
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "0.1.0",
        "features": {
            "supabase_auth": check_supabase_connection()["supabase_configured"],
            "ai_recommendations": True,
            "solana_payments": True,
            "real_time_messaging": True,
        }
    }


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
