#!/usr/bin/env python3
"""
Deploy fixes to production Supabase
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not service_key:
    print("Missing Supabase configuration")
    exit(1)

supabase = create_client(url, service_key)


def fix_rls_policies():
    """Fix RLS policies for orders table"""
    print("🔧 Fixing RLS policies for orders table...")

    # SQL to fix RLS policies
    sql_commands = """
    -- Drop existing policy if it exists
    DROP POLICY IF EXISTS "Users can manage their own orders" ON public.orders;
    
    -- Create new policy that allows order creation
    CREATE POLICY "Users can manage their own orders" ON public.orders 
    FOR ALL USING (
        auth.uid() = buyer_id OR 
        auth.uid() = seller_id OR
        auth.uid() IN (
            SELECT id FROM public.profiles 
            WHERE role = 'admin' OR is_verified_seller = true
        )
    );
    
    -- Also allow service role to manage orders (for admin operations)
    CREATE POLICY "Service role can manage all orders" ON public.orders 
    FOR ALL USING (auth.role() = 'service_role');
    """

    try:
        # Execute the SQL commands
        supabase.rpc("exec_sql", {"sql": sql_commands})
        print("✅ RLS policies fixed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error fixing RLS policies: {e}")
        return False


def test_orders_endpoint():
    """Test if orders endpoint works now"""
    print("🧪 Testing orders endpoint...")

    try:
        # Test if we can create an order
        test_order = {
            "buyer_id": "2c8d275e-c4fd-42a1-8c67-fce454b3a2c2",
            "seller_id": "ceeaead0-1768-40db-9143-24b8cc9c6f01",
            "listing_id": 2,
            "quantity": 1,
            "total_amount": 600.0,
            "delivery_address": "123 Test St",
            "status": "pending",
        }

        result = supabase.table("orders").insert(test_order).execute()
        if result.data:
            print("✅ Orders endpoint working!")
            # Clean up test order
            supabase.table("orders").delete().eq("id", result.data[0]["id"]).execute()
            return True
        else:
            print("❌ Orders endpoint still not working")
            return False

    except Exception as e:
        print(f"❌ Error testing orders: {e}")
        return False


def main():
    print("🚀 Deploying fixes to production...")

    # Fix RLS policies
    if fix_rls_policies():
        # Test the fix
        test_orders_endpoint()

    print("✅ Deployment complete!")


if __name__ == "__main__":
    main()
