import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Only create client if both URL and key are provided
if url and key:
    supabase: Client = create_client(url, key)
else:
    supabase: Client = None
    if not url:
        print("WARNING: SUPABASE_URL environment variable not set")
    if not key:
        print("WARNING: SUPABASE_SERVICE_ROLE_KEY environment variable not set")
