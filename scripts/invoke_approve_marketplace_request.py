import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def main():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get(
        "SUPABASE_ANON_KEY"
    )  # Use anon key for client-side operations
    supabase: Client = create_client(url, key)

    # Authenticate as the admin user
    admin_email = "admin@example.com"
    admin_password = "password123"
    print(f"Authenticating as admin user: {admin_email}")
    response = supabase.auth.sign_in_with_password(
        {"email": admin_email, "password": admin_password}
    )

    if not response.session:
        print("Error authenticating admin user:", response)
        return

    print("Admin user authenticated.")

    # The access token is automatically set in the client after sign-in

    # Replace with the ID of the marketplace request you want to approve
    request_id_to_approve = 1  # Replace with the actual ID

    print(
        f"Invoking Edge Function to approve marketplace request ID: {request_id_to_approve}"
    )
    response = supabase.functions.invoke(
        "approve-marketplace-request",
        invoke_options={"body": {"request_id": request_id_to_approve}},
    )

    print("Edge Function response:", response)


if __name__ == "__main__":
    main()
