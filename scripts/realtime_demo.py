import os
import time
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def main():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get(
        "SUPABASE_ANON_KEY"
    )  # Use anon key for client-side subscriptions
    supabase: Client = create_client(url, key)

    def callback(payload):
        print("New message received:", payload)

    print("Listening for new messages...")
    subscription = (
        supabase.realtime.channel("public:messages")
        .on("postgres_changes", callback, "*")
        .subscribe()
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping listener...")
        subscription.unsubscribe()


if __name__ == "__main__":
    main()
