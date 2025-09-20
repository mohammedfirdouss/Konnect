import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Only create client if both URL and key are provided
if url and key:
    supabase: Client = create_client(url, key)
else:
    supabase: Client = None
