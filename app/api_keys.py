import os

# Load keys from environment variable (comma separated) if available
env_keys = os.environ.get("YOUTUBE_API_KEYS")
single_key = os.environ.get("YOUTUBE_API_KEY")

API_KEYS = []
if env_keys:
    API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()]
elif single_key:
    API_KEYS = [single_key.strip()]

current = 0

def get_api_key():
    global current
    if not API_KEYS:
        # Prevent crash if imported but not used, but error if called
        print("Warning: No YOUTUBE_API_KEYS found in environment.")
        return None
    
    key = API_KEYS[current]
    current = (current + 1) % len(API_KEYS)
    return key

def log_api_usage(key, units):
    from app.db import api_usage
    from datetime import datetime
    
    api_usage.update_one(
        {"key": key, "date": datetime.now().strftime("%Y-%m-%d")},
        {"$inc": {"units": units}},
        upsert=True
    )
