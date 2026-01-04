import os

# Use environment variables for Render deployment
# Local fallback provided for testing
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "youtube_music")

LANGUAGES = {
    "hindi": ["hindi song", "bollywood song"],
    "telugu": ["telugu song", "tollywood song"],
    "tamil": ["tamil song", "kollywood song"],
    "english": ["english song", "official music video"]
}

MOODS = {
    "romantic": ["love", "romantic", "melody"],
    "sad": ["sad", "emotional", "heartbreak"],
    "party": ["party", "dance", "dj"],
    "devotional": ["devotional", "bhajan", "god"],
    "lofi": ["lofi", "chill", "slow"]
}
