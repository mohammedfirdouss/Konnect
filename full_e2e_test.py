import requests
import time
import json
import os

# --- Configuration ---
BASE_URL = "https://konnect-h72p.onrender.com"
# To hold the access token for the primary test user
USER_1_TOKEN = None
# To hold the access token and ID for the secondary test user
USER_2_TOKEN = None
USER_2_ID = None

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
    except (json.JSONDecodeError, AttributeError):
        print("Response Body (not JSON):")
        print(response.text)

def register_and_login(user_number):
    """Registers a new user and logs them in to get an access token."""
    print_step(f"Register and Login User {user_number}")
    timestamp = int(time.time()) + user_number
    user_details = {
        "username": f"testuser_{timestamp}",
        "email": f"testuser_{timestamp}@example.edu",
        "full_name": f"E2E Test User {user_number}",
        "password": "securePassword123"
    }
    
    # Registration
    print(f"--> Registering with email: {user_details['email']}")
    reg_response = requests.post(f"{BASE_URL}/auth/register", json=user_details)
    if reg_response.status_code != 200:
        print("❌ Registration failed.")
        print_response(reg_response)
        return None, None
    
    user_id = reg_response.json()["user"]["id"]
    print("--> Registration successful.")

    # Login
    print("--> Logging in...")
    login_credentials = {"email": user_details["email"], "password": user_details["password"]}
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_credentials)
    
    if login_response.status_code == 200 and "access_token" in login_response.json():
        access_token = login_response.json()["access_token"]
        print(f"--> Login successful for User {user_number}.")
        return access_token, user_id
    else:
        print("❌ Login failed.")
        print_response(login_response)
        return None, None

# --- Test Functions ---

def test_user_endpoints(token):
    """Tests fetching and updating a user profile."""
    if not token:
        return
    print_step("Test User Endpoints (Get & Update Profile)")
    headers = {"Authorization": f"Bearer {token}"}

    # Get current user profile summary (from auth data)
    print("--> Fetching user summary (/users/me)...")
    summary_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print_response(summary_response)
    assert summary_response.status_code == 200, "Failed to get user summary"
    print("--> User summary fetched successfully.")

    # Attempt to fetch extended profile details (may not exist yet)
    print("--> Fetching extended profile (/users/me/profile)...")
    profile_response = requests.get(f"{BASE_URL}/users/me/profile", headers=headers)
    print_response(profile_response)

    if profile_response.status_code == 200:
        print("--> Extended profile exists.")
    elif profile_response.status_code == 404:
        print("⚠️  Extended profile not found (expected if Supabase profile row hasn't been created yet). Continuing tests without update.")
        return
    else:
        raise AssertionError("Unexpected response fetching extended profile")

    # Update user profile (only if profile exists)
    print("--> Updating user profile...")
    update_data = {"full_name": "E2E Test User (Updated)"}
    update_response = requests.put(
        f"{BASE_URL}/users/me/profile", headers=headers, json=update_data
    )
    print_response(update_response)

    if update_response.status_code == 200:
        updated_profile = update_response.json().get("profile", {})
        assert (
            updated_profile.get("full_name") == "E2E Test User (Updated)"
        ), "Full name was not updated"
        print("--> Profile updated successfully.")
    elif update_response.status_code == 404:
        print("⚠️  Profile update skipped because profile does not exist.")
    else:
        raise AssertionError("Failed to update user profile")

def test_marketplace_endpoints():
    """Tests fetching marketplace data."""
    print_step("Test Marketplace Endpoints")
    
    # List all marketplaces
    print("--> Fetching all marketplaces...")
    list_response = requests.get(f"{BASE_URL}/marketplaces/")
    print_response(list_response)
    assert list_response.status_code == 200, "Failed to list marketplaces"
    marketplaces = list_response.json()
    assert len(marketplaces) > 0, "No marketplaces found"
    print("--> Marketplaces listed successfully.")

    # Get details for the first marketplace
    marketplace_id = marketplaces[0]['id']
    print(f"--> Fetching details for marketplace ID {marketplace_id}...")
    detail_response = requests.get(f"{BASE_URL}/marketplaces/{marketplace_id}")
    print_response(detail_response)
    assert detail_response.status_code == 200, "Failed to get marketplace details"
    print("--> Marketplace details fetched successfully.")

def test_listing_lifecycle(token):
    """Tests the full lifecycle of a listing: create, get, update, search, delete."""
    if not token: return
    print_step("Test Full Listing Lifecycle")
    headers = {"Authorization": f"Bearer {token}"}
    timestamp = int(time.time())
    listing_title = f"Vintage University Hoodie - Test {timestamp}"

    # 1. Create Listing
    print("--> 1. Creating new listing...")
    listing_data = {
        "title": listing_title,
        "description": "A high-quality hoodie from the E2E test.",
        "price": 45.99, "category": "Apparel", "marketplace_id": 1
    }
    create_response = requests.post(f"{BASE_URL}/listings/", headers=headers, json=listing_data)
    print_response(create_response)
    assert create_response.status_code == 201, "Listing creation failed"
    listing_id = create_response.json()["id"]
    print(f"--> Listing created with ID: {listing_id}")

    # 2. Get Listing Details
    print("\n--> 2. Fetching listing details...")
    get_response = requests.get(f"{BASE_URL}/listings/{listing_id}")
    print_response(get_response)
    assert get_response.status_code == 200, "Failed to fetch listing details"

    # 3. Update Listing
    print("\n--> 3. Updating listing...")
    update_data = {"price": 39.99, "description": "A high-quality hoodie (on sale)."}
    update_response = requests.put(f"{BASE_URL}/listings/{listing_id}", headers=headers, json=update_data)
    print_response(update_response)
    assert update_response.status_code == 200, "Failed to update listing"
    assert update_response.json()["price"] == 39.99, "Listing price was not updated"

    # 4. Search for Listing
    print("\n--> 4. Searching for listing...")
    search_response = requests.get(f"{BASE_URL}/products/search", params={"query": listing_title})
    print_response(search_response)
    assert search_response.status_code == 200, "Search request failed"
    assert search_response.json().get("total_count", 0) > 0, "Search failed to find new listing"
    print("--> Search successful.")

    # 5. Delete Listing
    print("\n--> 5. Deleting listing...")
    delete_response = requests.delete(f"{BASE_URL}/listings/{listing_id}", headers=headers)
    print(f"Status Code: {delete_response.status_code}")
    assert delete_response.status_code == 204, "Failed to delete listing"
    print("--> Listing deleted successfully.")
    
    return create_response.json() # Return original listing for other tests

def test_messaging_flow(sender_token, recipient_id):
    """Tests sending a message and retrieving threads."""
    if not sender_token or not recipient_id: return
    print_step("Test Messaging Flow")
    headers = {"Authorization": f"Bearer {sender_token}"}

    # Send message
    print(f"--> Sending message to user ID: {recipient_id}")
    message_data = {"recipient_id": recipient_id, "content": "Hello! Interested in your item."}
    send_response = requests.post(f"{BASE_URL}/messages/", headers=headers, json=message_data)
    print_response(send_response)
    assert send_response.status_code == 200, "Failed to send message"
    print("--> Message sent successfully.")

    # Get message threads
    print("--> Fetching message threads...")
    threads_response = requests.get(f"{BASE_URL}/messages/threads", headers=headers)
    print_response(threads_response)
    assert threads_response.status_code == 200, "Failed to get message threads"
    assert threads_response.json().get("total_count", 0) > 0, "Message thread not found"
    print("--> Message threads fetched successfully.")

def test_order_flow(buyer_token, listing):
    """Tests creating an order for a listing."""
    if not buyer_token or not listing: return
    print_step("Test Order Creation Flow")
    headers = {"Authorization": f"Bearer {buyer_token}"}
    
    print(f"--> Creating order for listing ID: {listing['id']}")
    order_data = {"listing_id": listing['id'], "quantity": 1}
    order_response = requests.post(f"{BASE_URL}/orders/", headers=headers, json=order_data)
    print_response(order_response)
    assert order_response.status_code == 200, "Failed to create order"
    print("--> Order created successfully.")

def test_ai_endpoints(token):
    """Tests various AI-powered endpoints."""
    if not token: return
    print_step("Test AI Endpoints")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. AI Recommendations
    print("--> 1. Testing AI Recommendations...")
    rec_response = requests.get(f"{BASE_URL}/ai/recommendations", headers=headers)
    print_response(rec_response)
    if rec_response.status_code != 200:
        print("❌ AI recommendations failed. Check API keys on Render.com.")
    else:
        print("✅ AI recommendations successful.")

    # 2. AI Price Suggestion
    print("\n--> 2. Testing AI Price Suggestion...")
    suggestion_data = {"title": "Used MacBook Pro 13-inch", "category": "Electronics"}
    price_response = requests.post(f"{BASE_URL}/ai/suggest-price", headers=headers, json=suggestion_data)
    print_response(price_response)
    if price_response.status_code != 200:
        print("❌ AI price suggestion failed.")
    else:
        print("✅ AI price suggestion successful.")

    # 3. AI Description Generation
    print("\n--> 3. Testing AI Description Generation...")
    description_data = {"title": "Used MacBook Pro 13-inch", "key_features": ["M1 Chip", "8GB RAM", "Good condition"]}
    desc_response = requests.post(f"{BASE_URL}/ai/generate-description", headers=headers, json=description_data)
    print_response(desc_response)
    if desc_response.status_code != 200:
        print("❌ AI description generation failed.")
    else:
        print("✅ AI description generation successful.")

# --- Main Execution ---

if __name__ == "__main__":
    print("🚀 Starting Konnect API Comprehensive End-to-End Test...")
    
    # Setup: Register and log in two separate users
    USER_1_TOKEN, _ = register_and_login(user_number=1)
    USER_2_TOKEN, USER_2_ID = register_and_login(user_number=2)

    if USER_1_TOKEN and USER_2_TOKEN:
        # Run test flows
        test_user_endpoints(USER_1_TOKEN)
        test_marketplace_endpoints()
        
        # Create a listing with User 2 to be bought by User 1
        listing_for_sale = test_listing_lifecycle(USER_2_TOKEN)
        
        test_messaging_flow(sender_token=USER_1_TOKEN, recipient_id=USER_2_ID)
        test_order_flow(buyer_token=USER_1_TOKEN, listing=listing_for_sale)
        
        test_ai_endpoints(USER_1_TOKEN)
    else:
        print("\n❌ Critical setup failed (user registration or login). Aborting tests.")

    print("\n🏁 Comprehensive test script finished.")