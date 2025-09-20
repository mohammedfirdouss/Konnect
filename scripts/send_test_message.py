import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def main():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY"
    )  # Use service role key for inserts
    supabase: Client = create_client(url, key)

    print("Sending a test message...")
    data, count = (
        supabase.table("messages")
        .insert(
            {
                "sender_id": "a_valid_user_id",  # Replace with a valid user ID from your profiles table
                "recipient_id": "another_valid_user_id",  # Replace with another valid user ID
                "content": "This is a real-time test message!",
            }
        )
        .execute()
    )

    print("Message sent:", data)


if __name__ == "__main__":
    main()
