#!/usr/bin/env python3
"""
Test script to verify Supabase connection and functionality
"""

import os
import sys

from dotenv import load_dotenv

from konnect.supabase_client import supabase, supabase_admin, check_supabase_connection

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔧 Testing Environment Variables...")

    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * 20}...{value[-4:]}")
        else:
            print(f"  ❌ {var}: Not set")
            missing_vars.append(var)

    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return False

    print("✅ All environment variables are set")
    return True


def test_supabase_clients():
    """Test Supabase client initialization"""
    print("\n🔧 Testing Supabase Client Initialization...")

    if supabase:
        print("  ✅ Public Supabase client initialized")
    else:
        print("  ❌ Public Supabase client failed to initialize")
        return False

    if supabase_admin:
        print("  ✅ Admin Supabase client initialized")
    else:
        print("  ❌ Admin Supabase client failed to initialize")
        return False

    return True


def test_supabase_connection():
    """Test actual connection to Supabase"""
    print("\n🔧 Testing Supabase Connection...")

    connection_status = check_supabase_connection()

    for key, value in connection_status.items():
        status_icon = "✅" if value else "❌"
        print(f"  {status_icon} {key}: {value}")

    return connection_status.get("connection_test") == "success"


def test_authentication_flow():
    """Test user registration and authentication"""
    print("\n🔧 Testing Authentication Flow...")

    if not supabase:
        print("  ❌ Supabase client not available")
        return False

    test_email = "test@example.com"
    test_password = "testpassword123"
    test_username = "testuser"

    try:
        # Test user registration
        print(f"  📝 Registering test user: {test_email}")
        response = supabase.auth.sign_up(
            {
                "email": test_email,
                "password": test_password,
                "options": {
                    "data": {"username": test_username, "full_name": "Test User"}
                },
            }
        )

        if response.user:
            print(f"  ✅ User registered: {response.user.id}")
            user_id = response.user.id
        else:
            print("  ❌ User registration failed")
            return False

        # Test user login
        print(f"  🔐 Testing login for: {test_email}")
        login_response = supabase.auth.sign_in_with_password(
            {"email": test_email, "password": test_password}
        )

        if login_response.session:
            print(
                f"  ✅ Login successful, token: {login_response.session.access_token[:20]}..."
            )

            # Test token validation
            print("  🔍 Testing token validation...")
            user_response = supabase.auth.get_user(login_response.session.access_token)

            if user_response.user:
                print(f"  ✅ Token validation successful: {user_response.user.id}")

                # Check if profile was created
                print("  👤 Checking profile creation...")
                profile_response = (
                    supabase.table("profiles")
                    .select("*")
                    .eq("id", user_id)
                    .single()
                    .execute()
                )

                if profile_response.data:
                    print(f"  ✅ Profile created: {profile_response.data['username']}")
                else:
                    print("  ❌ Profile not found")
                    return False

            else:
                print("  ❌ Token validation failed")
                return False
        else:
            print("  ❌ Login failed")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Authentication test failed: {e}")
        return False


def test_database_operations():
    """Test basic database operations"""
    print("\n🔧 Testing Database Operations...")

    if not supabase:
        print("  ❌ Supabase client not available")
        return False

    try:
        # Test reading marketplaces
        print("  📖 Testing marketplace read...")
        marketplace_response = (
            supabase.table("marketplaces").select("*").limit(5).execute()
        )
        print(f"  ✅ Found {len(marketplace_response.data)} marketplaces")

        # Test reading listings
        print("  📖 Testing listings read...")
        listings_response = supabase.table("listings").select("*").limit(5).execute()
        print(f"  ✅ Found {len(listings_response.data)} listings")

        # Test reading profiles
        print("  📖 Testing profiles read...")
        profiles_response = supabase.table("profiles").select("*").limit(5).execute()
        print(f"  ✅ Found {len(profiles_response.data)} profiles")

        return True

    except Exception as e:
        print(f"  ❌ Database operations test failed: {e}")
        return False


def test_rls_policies():
    """Test Row Level Security policies"""
    print("\n🔧 Testing RLS Policies...")

    if not supabase:
        print("  ❌ Supabase client not available")
        return False

    try:
        # Test public read access to marketplaces
        print("  🔒 Testing public marketplace access...")
        response = supabase.table("marketplaces").select("*").limit(1).execute()
        print(f"  ✅ Public marketplace access: {len(response.data)} records")

        # Test public read access to listings
        print("  🔒 Testing public listings access...")
        response = supabase.table("listings").select("*").limit(1).execute()
        print(f"  ✅ Public listings access: {len(response.data)} records")

        return True

    except Exception as e:
        print(f"  ❌ RLS policies test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Supabase Connection and Configuration Test")
    print("=" * 60)

    tests = [
        ("Environment Variables", test_environment_variables),
        ("Client Initialization", test_supabase_clients),
        ("Connection Test", test_supabase_connection),
        ("Authentication Flow", test_authentication_flow),
        ("Database Operations", test_database_operations),
        ("RLS Policies", test_rls_policies),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

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
        print("🎉 All tests passed! Supabase is properly configured.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
