from pymongo import MongoClient
from app.config import MONGO_URI, DB_NAME

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    songs = db.songs
    api_usage = db.api_usage
    channels = db.channels
except Exception as e:
    print(f"Database connection error: {e}")
    # Fallback/Mock for no DB environment if needed, or re-raise
    raise e
