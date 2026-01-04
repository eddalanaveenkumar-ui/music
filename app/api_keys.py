import os

# Load keys from environment variable (comma separated) if available
env_keys = os.environ.get("YOUTUBE_API_KEYS")

if env_keys:
    API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()]
else:
    # Fallback to hardcoded list (User must update this or set env var)
    API_KEYS = [
        "YOUR_API_KEY_1",
        "YOUR_API_KEY_2",
        "YOUR_API_KEY_3",
        "YOUR_API_KEY_4"
    ]

current = 0

def get_api_key():
    global current
    if not API_KEYS:
        raise Exception("No API keys provided")
    
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
