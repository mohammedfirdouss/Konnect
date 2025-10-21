import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
# Load environment from the same file as main.py
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Konnect.env")
load_dotenv(env_path)

logger = logging.getLogger(__name__)

url: str = os.environ.get("SUPABASE_URL")
anon_key: str = os.environ.get("SUPABASE_ANON_KEY")
service_role_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Create clients for different use cases
if url and anon_key:
    # Client for public operations (authentication, public data)
    supabase: Client = create_client(url, anon_key)
    logger.info("Supabase client initialized with anon key")
else:
    supabase: Client = None
    logger.warning("Supabase client not initialized - missing URL or anon key")

if url and service_role_key:
    # Admin client for service operations (bypasses RLS)
    supabase_admin: Client = create_client(url, service_role_key)
    logger.info("Supabase admin client initialized")
else:
    supabase_admin: Client = None
    logger.warning("Supabase admin client not initialized - missing service role key")


# Health check function
def check_supabase_connection() -> dict:
    """Check Supabase connection status"""
    status = {
        "supabase_configured": supabase is not None,
        "admin_configured": supabase_admin is not None,
        "url_configured": url is not None,
        "anon_key_configured": anon_key is not None,
        "service_key_configured": service_role_key is not None,
    }

    if supabase:
        try:
            # Test connection with a simple query
            supabase.table("profiles").select("id").limit(1).execute()
            status["connection_test"] = "success"
        except Exception as e:
            status["connection_test"] = f"failed: {str(e)}"
            logger.error(f"Supabase connection test failed: {e}")

    return status
