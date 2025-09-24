#!/usr/bin/env python3
"""
Test script to verify Render deployment configuration and database connectivity
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


def test_environment_for_render():
    """Test environment variables for Render deployment"""
    print("🔧 Testing Render Environment Configuration...")
    
    # Required environment variables for Render
    render_vars = {
        "DATABASE_URL": "PostgreSQL connection string",
        "SECRET_KEY": "Application secret key",
        "PYTHONPATH": "Python path configuration",
        "ENVIRONMENT": "Environment setting",
        "SUPABASE_URL": "Supabase project URL",
        "SUPABASE_ANON_KEY": "Supabase anonymous key",
        "SUPABASE_SERVICE_ROLE_KEY": "Supabase service role key",
    }
    
    missing_vars = []
    configured_vars = []
    
    for var, description in render_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var:
                display_value = f"{'*' * 20}...{value[-4:]}"
            elif "URL" in var:
                display_value = f"{value[:30]}..."
            else:
                display_value = value
            
            print(f"  ✅ {var}: {display_value}")
            configured_vars.append(var)
        else:
            print(f"  ❌ {var}: Not set ({description})")
            missing_vars.append(var)
    
    # Optional variables
    optional_vars = ["REDIS_URL", "GOOGLE_API_KEY", "LOG_LEVEL"]
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ℹ️  {var}: Configured (optional)")
        else:
            print(f"  ⚪ {var}: Not set (optional)")
    
    if missing_vars:
        print(f"\n⚠️  Missing required variables: {', '.join(missing_vars)}")
        return False
    
    print(f"\n✅ All required environment variables configured ({len(configured_vars)}/{len(render_vars)})")
    return True


def test_database_connection():
    """Test PostgreSQL database connection"""
    print("\n🔧 Testing PostgreSQL Database Connection...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("  ❌ DATABASE_URL not configured")
        return False
    
    try:
        # Parse the database URL
        parsed = urlparse(database_url)
        print(f"  📍 Database host: {parsed.hostname}")
        print(f"  📍 Database port: {parsed.port}")
        print(f"  📍 Database name: {parsed.path[1:] if parsed.path else 'N/A'}")
        print(f"  📍 Database user: {parsed.username}")
        
        # Test connection
        print("  🔌 Testing connection...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"  ✅ Connected to PostgreSQL: {version[:50]}...")
        
        # Test table existence (if any)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"  📊 Found {len(tables)} tables:")
            for table in tables[:10]:  # Show first 10 tables
                print(f"    - {table[0]}")
            if len(tables) > 10:
                print(f"    ... and {len(tables) - 10} more")
        else:
            print("  📊 No tables found (fresh database)")
        
        cursor.close()
        conn.close()
        
        print("  ✅ Database connection test successful")
        return True
        
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False


def test_application_startup():
    """Test that the application can start with current configuration"""
    print("\n🔧 Testing Application Startup...")
    
    try:
        # Import the main app
        from konnect.main import app
        print("  ✅ FastAPI application imported successfully")
        
        # Test that routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/metrics", "/auth/register", "/auth/token"]
        
        missing_routes = []
        for route in expected_routes:
            if route in routes:
                print(f"  ✅ Route registered: {route}")
            else:
                print(f"  ❌ Route missing: {route}")
                missing_routes.append(route)
        
        if missing_routes:
            print(f"  ⚠️  Missing routes: {', '.join(missing_routes)}")
            return False
        
        print(f"  ✅ All expected routes registered ({len(expected_routes)} routes)")
        return True
        
    except Exception as e:
        print(f"  ❌ Application startup test failed: {e}")
        return False


def test_render_specific_config():
    """Test Render-specific configuration"""
    print("\n🔧 Testing Render-Specific Configuration...")
    
    # Check Python path
    pythonpath = os.getenv("PYTHONPATH")
    if pythonpath:
        print(f"  ✅ PYTHONPATH configured: {pythonpath}")
    else:
        print("  ⚠️  PYTHONPATH not set (may cause import issues)")
    
    # Check environment setting
    environment = os.getenv("ENVIRONMENT", "development")
    print(f"  ✅ Environment: {environment}")
    
    # Check port configuration
    port = os.getenv("PORT", "8000")
    print(f"  ✅ Port: {port}")
    
    # Check if we're likely running on Render
    render_service_name = os.getenv("RENDER_SERVICE_NAME")
    if render_service_name:
        print(f"  ✅ Running on Render service: {render_service_name}")
        
        # Additional Render environment info
        render_region = os.getenv("RENDER_REGION")
        if render_region:
            print(f"  ✅ Render region: {render_region}")
            
        render_git_commit = os.getenv("RENDER_GIT_COMMIT")
        if render_git_commit:
            print(f"  ✅ Git commit: {render_git_commit[:8]}")
    else:
        print("  ℹ️  Not running on Render (local development)")
    
    return True


def test_health_endpoint():
    """Test the health endpoint functionality"""
    print("\n🔧 Testing Health Endpoint...")
    
    try:
        import requests
        
        # Determine the base URL
        if os.getenv("RENDER_SERVICE_NAME"):
            # Running on Render
            service_name = os.getenv("RENDER_SERVICE_NAME")
            base_url = f"https://{service_name}.onrender.com"
        else:
            # Local development
            port = os.getenv("PORT", "8000")
            base_url = f"http://localhost:{port}"
        
        print(f"  🌐 Testing health endpoint: {base_url}/health")
        
        # Make request to health endpoint
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"  ✅ Health check passed: {health_data.get('status', 'unknown')}")
            
            # Display health details
            if 'supabase' in health_data:
                supabase_status = health_data['supabase']
                print(f"  📊 Supabase configured: {supabase_status.get('supabase_configured', False)}")
                print(f"  📊 Database connected: {supabase_status.get('connection_test') == 'success'}")
            
            return True
        else:
            print(f"  ❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  ⚠️  Could not connect to application (not running or network issue)")
        return False
    except Exception as e:
        print(f"  ❌ Health endpoint test failed: {e}")
        return False


def generate_deployment_checklist():
    """Generate a deployment checklist for Render"""
    print("\n📋 Render Deployment Checklist:")
    print("=" * 50)
    
    checklist_items = [
        "✅ Create Render account and connect GitHub repository",
        "✅ Create PostgreSQL database service on Render",
        "✅ Create Redis service on Render (optional, for caching)",
        "✅ Create Web Service with Python environment",
        "✅ Configure build command: 'pip install --upgrade pip && pip install -r requirements.txt'",
        "✅ Configure start command: 'uvicorn konnect.main:app --host 0.0.0.0 --port $PORT'",
        "✅ Set health check path: '/health'",
        "✅ Configure environment variables in Render dashboard:",
        "   - DATABASE_URL (from PostgreSQL service)",
        "   - REDIS_URL (from Redis service)",
        "   - SECRET_KEY (generate random value)",
        "   - SUPABASE_URL (from your Supabase project)",
        "   - SUPABASE_ANON_KEY (from your Supabase project)",
        "   - SUPABASE_SERVICE_ROLE_KEY (from your Supabase project)",
        "   - ENVIRONMENT=production",
        "   - PYTHONPATH=/opt/render/project/src",
        "✅ Deploy the service",
        "✅ Test the deployed application health endpoint",
        "✅ Verify database connectivity",
        "✅ Test authentication endpoints",
        "✅ Monitor logs for any issues",
    ]
    
    for item in checklist_items:
        print(f"  {item}")
    
    print("\n🔗 Useful Render Documentation:")
    print("  - Web Services: https://render.com/docs/web-services")
    print("  - Environment Variables: https://render.com/docs/environment-variables")
    print("  - PostgreSQL: https://render.com/docs/databases")
    print("  - Redis: https://render.com/docs/redis")


def main():
    """Run all tests and generate deployment information"""
    print("🚀 Konnect Render Deployment Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", test_environment_for_render),
        ("Database Connection", test_database_connection),
        ("Application Startup", test_application_startup),
        ("Render Configuration", test_render_specific_config),
        ("Health Endpoint", test_health_endpoint),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Generate deployment checklist
    generate_deployment_checklist()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status_icon = "✅" if result else "❌"
        print(f"  {status_icon} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for Render deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)