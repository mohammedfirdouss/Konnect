#!/usr/bin/env python3
"""
Setup script for creating admin users in Konnect
Run this script to create admin users with proper roles
"""

import os
import sys
from supabase import create_client, Client


def create_admin_user():
    """Create an admin user in Supabase"""

    # Get Supabase credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print(
            "❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required"
        )
        print("Please set these in your .env file or environment")
        return False

    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        # Get admin credentials from environment or prompt
        admin_email = os.getenv("ADMIN_EMAIL", "admin@konnect.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123456")
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_full_name = os.getenv("ADMIN_FULL_NAME", "System Administrator")

        print("👤 Creating admin user:")
        print(f"   Email: {admin_email}")
        print(f"   Username: {admin_username}")
        print(f"   Full Name: {admin_full_name}")

        # Create user in Supabase Auth
        try:
            auth_response = supabase.auth.admin.create_user(
                {
                    "email": admin_email,
                    "password": admin_password,
                    "email_confirm": True,  # Auto-confirm email
                    "user_metadata": {
                        "username": admin_username,
                        "full_name": admin_full_name,
                        "role": "admin",
                    },
                }
            )

            if auth_response.user:
                user_id = auth_response.user.id
                print(f"✅ Created admin user with ID: {user_id}")

                # Create profile in profiles table
                profile_data = {
                    "id": user_id,
                    "username": admin_username,
                    "full_name": admin_full_name,
                    "email": admin_email,
                    "role": "admin",
                    "is_verified_seller": True,
                    "is_admin": True,
                }

                try:
                    supabase.table("profiles").insert(profile_data).execute()
                    print("✅ Created admin profile")

                except Exception as e:
                    print(f"⚠️  Warning: Could not create profile: {e}")
                    print("You may need to create the profile manually in Supabase")

                print("\n🎉 Admin user created successfully!")
                print(f"📧 Email: {admin_email}")
                print(f"🔑 Password: {admin_password}")
                print(f"🆔 User ID: {user_id}")

                return True

            else:
                print("❌ Failed to create admin user")
                return False

        except Exception as e:
            if "already registered" in str(e).lower():
                print(f"⚠️  User {admin_email} already exists")
                print("Updating user role to admin...")

                # Try to update existing user
                try:
                    # Get user by email
                    users_response = supabase.auth.admin.list_users()
                    existing_user = None
                    for user in users_response:
                        if user.email == admin_email:
                            existing_user = user
                            break

                    if existing_user:
                        user_id = existing_user.id

                        # Update user metadata
                        supabase.auth.admin.update_user_by_id(
                            user_id,
                            {
                                "user_metadata": {
                                    "username": admin_username,
                                    "full_name": admin_full_name,
                                    "role": "admin",
                                }
                            },
                        )

                        # Update profile
                        profile_data = {
                            "role": "admin",
                            "is_admin": True,
                            "is_verified_seller": True,
                        }

                        supabase.table("profiles").update(profile_data).eq(
                            "id", user_id
                        ).execute()

                        print("✅ Updated existing user to admin role")
                        print(f"🆔 User ID: {user_id}")
                        return True
                    else:
                        print("❌ Could not find existing user")
                        return False

                except Exception as update_error:
                    print(f"❌ Error updating user: {update_error}")
                    return False
            else:
                print(f"❌ Error creating admin user: {e}")
                return False

    except Exception as e:
        print(f"❌ Error setting up admin user: {e}")
        return False


def setup_admin_policies():
    """Setup RLS policies for admin access"""
    print("\n🔒 Admin RLS Policies to add in Supabase SQL Editor:")
    print("=" * 60)

    policies = """
-- Policy 1: Allow admins to access admin endpoints
CREATE POLICY "Allow admin access to admin endpoints" ON profiles
FOR ALL USING (
    auth.role() = 'authenticated' AND
    (auth.jwt() ->> 'user_metadata' ->> 'role') = 'admin'
);

-- Policy 2: Allow admins to view all profiles
CREATE POLICY "Allow admins to view all profiles" ON profiles
FOR SELECT USING (
    auth.role() = 'authenticated' AND
    (auth.jwt() ->> 'user_metadata' ->> 'role') = 'admin'
);

-- Policy 3: Allow admins to update any profile
CREATE POLICY "Allow admins to update any profile" ON profiles
FOR UPDATE USING (
    auth.role() = 'authenticated' AND
    (auth.jwt() ->> 'user_metadata' ->> 'role') = 'admin'
);

-- Policy 4: Allow admins to manage marketplace requests
CREATE POLICY "Allow admins to manage marketplace requests" ON marketplace_requests
FOR ALL USING (
    auth.role() = 'authenticated' AND
    (auth.jwt() ->> 'user_metadata' ->> 'role') = 'admin'
);

-- Policy 5: Allow admins to manage all listings
CREATE POLICY "Allow admins to manage all listings" ON listings
FOR ALL USING (
    auth.role() = 'authenticated' AND
    (auth.jwt() ->> 'user_metadata' ->> 'role') = 'admin'
);
"""

    print(policies)
    print("=" * 60)
    print("📋 Instructions:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Run the above policies")
    print("4. Test admin endpoints with the created admin user")


def main():
    """Main setup function"""
    print("🚀 Setting up Admin User for Konnect...")
    print("=" * 50)

    success = create_admin_user()

    if success:
        setup_admin_policies()
        print("\n🎉 Admin setup completed successfully!")
        print("\nNext steps:")
        print("1. Add the RLS policies in Supabase SQL Editor")
        print("2. Test admin endpoints with the admin credentials")
        print("3. Update your frontend to handle admin authentication")
    else:
        print("\n❌ Admin setup failed!")
        print("Please check your Supabase credentials and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
