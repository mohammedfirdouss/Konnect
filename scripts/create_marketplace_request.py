import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def main():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    # Replace with a valid user ID, for example, the admin user ID from the previous script
    requester_id = "a_valid_user_id"

    print("Creating a new marketplace request...")
    data, count = (
        supabase.table("marketplace_requests")
        .insert(
            {
                "university_name": "Test University",
                "university_domain": "test.edu",
                "contact_email": "test@test.edu",
                "description": "A marketplace for students of Test University",
                "requested_by": requester_id,
            }
        )
        .execute()
    )

    if data:
        print("Marketplace request created:", data[1][0])
        print("Please use the ID from the response to test the Edge Function.")
    else:
        print("Error creating marketplace request.")


if __name__ == "__main__":
    main()
