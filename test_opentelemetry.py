"""
Tests for OpenTelemetry integration
"""

import json
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_metrics_endpoint_exists():
    """Test that the /metrics endpoint exists and returns Prometheus metrics"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_metrics_content():
    """Test that the metrics endpoint returns Prometheus format content"""
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    
    # Check for basic Prometheus metrics format
    assert "# HELP" in content
    assert "# TYPE" in content
    
    # Check for HTTP server metrics (these are provided by OpenTelemetry FastAPI instrumentation)
    assert "http_server_duration_milliseconds" in content or "http_" in content


def test_http_request_instrumentation():
    """Test that HTTP requests are being instrumented"""
    # Make a request to trigger instrumentation
    response = client.get("/")
    assert response.status_code == 200
    
    # Check metrics endpoint for HTTP instrumentation
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    
    # Verify HTTP metrics are present
    metrics_content = metrics_response.text
    assert "http_server" in metrics_content.lower()


def test_root_endpoint_with_opentelemetry():
    """Test that the root endpoint still works with OpenTelemetry instrumentation"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Konnect - Campus Tools with SolanaPay"


def test_health_endpoint_with_opentelemetry():
    """Test that the health endpoint still works with OpenTelemetry instrumentation"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "konnect"


def test_docs_endpoint_with_opentelemetry():
    """Test that the docs endpoint still works with OpenTelemetry instrumentation"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_json_with_opentelemetry():
    """Test that the OpenAPI JSON endpoint includes the metrics endpoint"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_data = response.json()
    
    # Check that metrics endpoint is documented
    assert "/metrics" in openapi_data["paths"]
    assert "get" in openapi_data["paths"]["/metrics"]