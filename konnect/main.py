"""
Main application module for Konnect
"""

import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from pythonjsonlogger import jsonlogger

from .database import create_tables
from .routers import auth, users, listings

# Configure OpenTelemetry Metrics
prometheus_reader = PrometheusMetricReader()
metrics.set_meter_provider(MeterProvider(metric_readers=[prometheus_reader]))

# Configure OpenTelemetry Tracing
trace.set_tracer_provider(TracerProvider())

# Configure structured JSON logging
def setup_logging():
    """Setup structured JSON logging"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create JSON formatter
    json_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    json_handler.setFormatter(formatter)
    logger.addHandler(json_handler)
    
    return logger

# Setup logging
logger = setup_logging()

app = FastAPI(
    title="Konnect", description="Campus Tools with SolanaPay", version="0.1.0"
)

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    logger.info("Starting up Konnect application")
    create_tables()
    logger.info("Database tables created successfully")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint requested")
    return {"message": "Welcome to Konnect - Campus Tools with SolanaPay"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "konnect"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    logger.info("Metrics endpoint requested")
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


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
