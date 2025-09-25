#!/usr/bin/env python3
"""
Setup script for Supabase Storage bucket for listing images
Run this script to create the required storage bucket and policies
"""

import os
import sys
from supabase import create_client, Client


def setup_storage_bucket():
    """Create Supabase storage bucket for listing images"""

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

        # Create storage bucket
        bucket_name = "listing_images"
        print(f"🪣 Creating storage bucket: {bucket_name}")

        # Check if bucket already exists
        try:
            buckets = supabase.storage.list_buckets()
            existing_buckets = [bucket.name for bucket in buckets]

            if bucket_name in existing_buckets:
                print(f"✅ Bucket '{bucket_name}' already exists")
            else:
                # Create new bucket
                supabase.storage.create_bucket(
                    bucket_name,
                    options={
                        "public": True,  # Make bucket public for image access
                        "file_size_limit": 10485760,  # 10MB limit
                        "allowed_mime_types": [
                            "image/jpeg",
                            "image/png",
                            "image/gif",
                            "image/webp",
                        ],
                    },
                )
                print(f"✅ Created bucket '{bucket_name}'")

        except Exception as e:
            print(f"❌ Error creating bucket: {e}")
            return False

        # Create RLS policies for the bucket
        print("🔒 Setting up storage policies...")

        # Policy 1: Allow authenticated users to upload images
        upload_policy = """
        CREATE POLICY "Allow authenticated users to upload images" ON storage.objects
        FOR INSERT WITH CHECK (
            auth.role() = 'authenticated' AND
            bucket_id = 'listing_images' AND
            (storage.foldername(name))[1] = auth.uid()::text
        );
        """

        # Policy 2: Allow public read access to images
        read_policy = """
        CREATE POLICY "Allow public read access to images" ON storage.objects
        FOR SELECT USING (bucket_id = 'listing_images');
        """

        # Policy 3: Allow users to delete their own images
        delete_policy = """
        CREATE POLICY "Allow users to delete their own images" ON storage.objects
        FOR DELETE USING (
            auth.role() = 'authenticated' AND
            bucket_id = 'listing_images' AND
            (storage.foldername(name))[1] = auth.uid()::text
        );
        """

        try:
            # Execute policies (these would need to be run in Supabase SQL editor)
            print("📝 Storage policies to add in Supabase SQL Editor:")
            print("\n" + "=" * 60)
            print("POLICY 1 - Upload Policy:")
            print(upload_policy)
            print("\nPOLICY 2 - Read Policy:")
            print(read_policy)
            print("\nPOLICY 3 - Delete Policy:")
            print(delete_policy)
            print("=" * 60)
            print("\n📋 Instructions:")
            print("1. Go to your Supabase dashboard")
            print("2. Navigate to SQL Editor")
            print("3. Run the above policies one by one")
            print("4. Or run them all at once")

        except Exception as e:
            print(
                f"⚠️  Note: Policies need to be added manually in Supabase dashboard: {e}"
            )

        print("\n✅ Storage setup completed!")
        print(f"📁 Bucket: {bucket_name}")
        print(f"🔗 Public URL: {supabase_url}/storage/v1/object/public/{bucket_name}/")

        return True

    except Exception as e:
        print(f"❌ Error setting up storage: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up Supabase Storage for Konnect...")
    print("=" * 50)

    success = setup_storage_bucket()

    if success:
        print("\n🎉 Storage setup completed successfully!")
        print("\nNext steps:")
        print("1. Add the storage policies in Supabase SQL Editor")
        print("2. Test image upload endpoints")
        print("3. Update your frontend to use the storage URLs")
    else:
        print("\n❌ Storage setup failed!")
        print("Please check your Supabase credentials and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
