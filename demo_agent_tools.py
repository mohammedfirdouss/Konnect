"""Demo script to showcase the agent tool functionality"""

import requests
import json
from datetime import datetime

def demo_agent_tools():
    """Demonstrate the agent tools functionality"""
    base_url = "http://localhost:8000"
    
    print("🚀 Konnect Agent Tools Demo")
    print("=" * 50)
    
    # Test 1: Check server health
    print("\n1. Testing server health...")
    response = requests.get(f"{base_url}/health")
    if response.status_code == 200:
        print("✅ Server is healthy")
        print(f"   Response: {response.json()}")
    else:
        print("❌ Server health check failed")
        return
    
    # Test 2: Get available agent tools
    print("\n2. Getting available agent tools...")
    response = requests.get(f"{base_url}/agent/tools")
    if response.status_code == 200:
        tools = response.json()
        print("✅ Agent tools available:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
            print(f"     Parameters: {tool['parameters']}")
    else:
        print("❌ Failed to get agent tools")
        return
    
    # Test 3: Get agent prompt
    print("\n3. Getting agent prompt...")
    response = requests.get(f"{base_url}/agent/prompt")
    if response.status_code == 200:
        prompt_data = response.json()
        prompt = prompt_data['prompt']
        print("✅ Agent prompt retrieved:")
        print(f"   Length: {len(prompt)} characters")
        print(f"   Contains 'get_user_activity': {'get_user_activity' in prompt}")
        print(f"   Contains 'recommendations': {'recommendations' in prompt}")
    else:
        print("❌ Failed to get agent prompt")
        return
    
    print("\n4. Testing the get_user_activity function...")
    print("   Note: This requires authentication, so we'll test the CRUD function directly")
    
    # Import and test the CRUD function
    try:
        from konnect.database import SessionLocal
        from konnect import crud, schemas, models
        
        # Create a test database session
        db = SessionLocal()
        
        # Create a test user
        user_data = schemas.UserCreate(
            username=f"demouser_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            email=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            full_name="Demo User",
            password="demopassword"
        )
        
        # Create user
        db_user = crud.create_user(db, user_data)
        print(f"   ✅ Created demo user: {db_user.username}")
        
        # Create a marketplace
        marketplace_data = schemas.MarketplaceCreate(
            name="Demo Marketplace",
            description="A demonstration marketplace"
        )
        db_marketplace = crud.create_marketplace(db, marketplace_data, db_user.id)
        print(f"   ✅ Created demo marketplace: {db_marketplace.name}")
        
        # Create a listing
        listing_data = schemas.ListingCreate(
            title="Demo Laptop",
            description="A demonstration laptop listing",
            price=899.99,
            category="electronics",
            marketplace_id=db_marketplace.id
        )
        db_listing = crud.create_listing(db, listing_data, db_user.id)
        print(f"   ✅ Created demo listing: {db_listing.title}")
        
        # Create a purchase
        purchase_data = schemas.PurchaseCreate(
            listing_id=db_listing.id,
            amount=899.99,
            status="completed",
            transaction_hash="demo_hash_12345"
        )
        db_purchase = crud.create_purchase(db, purchase_data, db_user.id)
        print(f"   ✅ Created demo purchase: ${db_purchase.amount}")
        
        # Create browsing history
        browsing_data = schemas.BrowsingHistoryCreate(
            listing_id=db_listing.id,
            action="view"
        )
        db_browsing = crud.create_browsing_history(db, browsing_data, db_user.id)
        print(f"   ✅ Created demo browsing history: {db_browsing.action}")
        
        # Test the get_user_activity function
        activity = crud.get_user_activity(db, db_user.id, limit=10)
        print(f"\n   📊 User Activity Summary:")
        print(f"      User ID: {activity.user_id}")
        print(f"      Purchases: {len(activity.purchases)}")
        print(f"      Browsing History: {len(activity.browsing_history)}")
        
        if activity.purchases:
            print(f"      Latest Purchase: ${activity.purchases[0].amount} - {activity.purchases[0].status}")
        
        if activity.browsing_history:
            print(f"      Latest Browse Action: {activity.browsing_history[0].action}")
        
        # Cleanup
        db.close()
        print(f"   ✅ Demo data created and activity retrieved successfully!")
        
    except Exception as e:
        print(f"   ❌ Error testing CRUD function: {str(e)}")
        return
    
    print("\n🎉 Demo completed successfully!")
    print("\n📋 Summary:")
    print("   ✅ Agent tool registry working")
    print("   ✅ get_user_activity function implemented")
    print("   ✅ Agent prompt with tool instructions created")
    print("   ✅ API endpoints for agent integration available")
    print("   ✅ Purchase and browsing history tracking working")
    
    print("\n📚 Available Endpoints:")
    print(f"   - GET  {base_url}/agent/tools        - List available tools")
    print(f"   - GET  {base_url}/agent/prompt       - Get agent prompt")
    print(f"   - POST {base_url}/agent/tools/{{name}} - Execute a tool (requires auth)")
    print(f"   - GET  {base_url}/agent/user-activity - Get user activity (requires auth)")

if __name__ == "__main__":
    demo_agent_tools()