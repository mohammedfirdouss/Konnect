import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def main():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    # Create a new user
    email = "admin@example.com"
    password = "password123"
    print(f"Creating admin user with email: {email}")
    response = supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {"data": {"username": "admin", "full_name": "Admin User"}},
        }
    )

    if not response.user:
        print("Error creating user:", response)
        return

    user_id = response.user.id
    print(f"User created with ID: {user_id}")

    # Update the user's role to 'admin' in the profiles table
    data, count = (
        supabase.table("profiles").update({"role": "admin"}).eq("id", user_id).execute()
    )

    if count:
        print("User role updated to admin.")
    else:
        print("Error updating user role.")


if __name__ == "__main__":
    main()
