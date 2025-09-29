import requests
import time
import json
import os

# --- Configuration ---
# The base URL for the production API.
BASE_URL = "https://konnect-h72p.onrender.com"

# --- Helper Functions ---

def print_step(title):
    """Prints a formatted step title."""
    print("\n" + "="*50)
    print(f"✅ Step: {title}")
    print("="*50)

def print_response(response):
    """Prints the status code and JSON response."""
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Response Body (not JSON):")
        print(response.text)

# --- Test Steps ---

def register_new_user():
    """
    Step 1: Register a new, unique user.
    A timestamp is used to ensure the email and username are always unique,
    allowing the script to be run multiple times without conflicts.
    """
    print_step("Register a New User")
    timestamp = int(time.time())
    user_details = {
        "username": f"testuser_{timestamp}",
        "email": f"testuser_{timestamp}@example.edu",
        "full_name": "E2E Test User",
        "password": "securePassword123"
    }
    
    print(f"Registering with email: {user_details['email']}")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=user_details
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print("✅ Registration successful.")
        return user_details
    else:
        print("❌ Registration failed.")
        return None

def login_user(user_details):
    """
    Step 2: Log in as the newly created user.
    This authenticates the user and retrieves a JWT access token required
    for accessing protected endpoints.
    """
    if not user_details:
        return None
        
    print_step("Log In User")
    login_credentials = {
        "email": user_details["email"],
        "password": user_details["password"]
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_credentials  # Use data for application/x-www-form-urlencoded
    )
    
    print_response(response)
    
    if response.status_code == 200 and "access_token" in response.json():
        access_token = response.json()["access_token"]
        print("✅ Login successful. Token obtained.")
        return access_token
    else:
        print("❌ Login failed.")
        return None

def create_listing(access_token):
    """
    Step 3: Create a new marketplace listing.
    This tests the ability of an authenticated user to create a new product,
    verifying a core feature of the marketplace.
    """
    if not access_token:
        return None

    print_step("Create a New Listing")
    timestamp = int(time.time())
    listing_data = {
        "title": f"Vintage University Hoodie - Test {timestamp}",
        "description": "A high-quality, comfortable hoodie from the E2E test script.",
        "price": 45.99,
        "category": "Apparel",
        "marketplace_id": 1  # Assuming marketplace with ID 1 exists
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.post(
        f"{BASE_URL}/listings/",
        headers=headers,
        json=listing_data
    )
    
    print_response(response)
    
    if response.status_code == 201:
        print("✅ Listing created successfully.")
        return response.json()
    else:
        print("❌ Listing creation failed.")
        return None

def search_for_listing(listing_data):
    """
    Step 4: Search for the newly created listing.
    This verifies that the search endpoint is working and that newly created
    items are indexed and discoverable.
    """
    if not listing_data:
        return

    print_step("Search for the New Listing")
    query = listing_data["title"]
    
    print(f"Searching for query: \"{query}\"")
    
    response = requests.get(
        f"{BASE_URL}/products/search",
        params={"query": query}
    )
    
    print_response(response)
    
    if response.status_code == 200 and response.json().get("total_count", 0) > 0:
        print("✅ Search successful. Listing found.")
    else:
        print("❌ Search failed or listing not found.")

def test_ai_recommendations(access_token):
    """
    Step 5: Test the AI recommendations endpoint.
    This checks the status of the AI service. It will fail if the API keys
    are not correctly configured in the production environment.
    """
    if not access_token:
        return

    print_step("Test AI Recommendations")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(
        f"{BASE_URL}/ai/recommendations",
        headers=headers,
        params={"limit": 5}
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print("✅ AI recommendations endpoint returned a successful response.")
    else:
        print("❌ AI recommendations endpoint failed. Check API keys on Render.com.")

# --- Main Execution ---

if __name__ == "__main__":
    print("🚀 Starting Konnect API End-to-End Test...")
    
    # Run the test steps in sequence
    user = register_new_user()
    token = login_user(user)
    new_listing = create_listing(token)
    search_for_listing(new_listing)
    test_ai_recommendations(token)
    
    print("\n🏁 Test script finished.")
