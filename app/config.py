import os

# Use environment variables for Render deployment
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "youtube_music")

# Quota management
QUOTA_PER_RUN = 50 # Number of videos to fetch per channel per run

# Channel IDs by Language
CHANNELS = {
    "hindi": [
        "UCq-Fj5jknLsUf-MWSy4_brA", # T-Series
        "UCFFbwnve3yF62-tVXkTyHqg", # Zee Music Company
        "UC56gTxNs4f9xZ7Pa2i5xNzg", # Sony Music India
        "UC1lvjqqm3gL3zZIcQ1jV3Mw", # Saregama Music
        "UCJrDMFOdv1I2rhe6b9cFvVQ", # Tips Official
        "UCt7sv-NKh44rHAEb-qCCxvA", # YRF Music
        "UCX6OQ3DkcsbYNE6H8uQQuVA"  # Shemaroo Filmi Gaane
    ],
    "telugu": [
        "UCnSqxrSfo1sK4WZ7nBpYW1Q", # Lahari Music Telugu
        "UCbTLwN10NoCU4WDzLf1JMOA", # T-Series Telugu
        "UCLsSLka8jODBozvi5VTQeaQ", # Zee Music South
        "UCwYy3m5y0cHqXxJZQn9hF_w"  # Sony Music South (Shared)
    ],
    "tamil": [
        "UCwYy3m5y0cHqXxJZQn9hF_w", # Sony Music South (Shared)
        "UC9C9J7K7q0rXqH8kN3a5sFg", # Think Music India
        "UCd460WUL4835Jd7OCEKfUcA", # Star Music India
        "UCZoho9z_Jib7N8Z4P_6iJkQ"  # T-Series Tamil
    ],
    "malayalam": [
        "UCuCjM7x3sGz4x7O3Z1J6fZw", # Manorama Music
        "UChRi1dpwnsZcIo1LSwzY0Iw", # Muzik247
        "UC3xFjzC1zv9b4h8kJ1YkZVQ"  # T-Series Malayalam
    ],
    "kannada": [
        "UCZ0kZ0wzFzDgq5ZP2pQb3Fg", # Saregama Kannada
        "UC8t1wV5t3Y7bJ0hM5cZ4nKw", # Lahari Music Kannada
        "UCbTLwN10NoCU4WDzLf1JMOA"  # T-Series Kannada (Likely shared or similar ID logic, using provided)
    ],
    "punjabi": [
        "UC4zWG9LccdWGUlF77LZ8toA", # T-Series Apna Punjab
        "UCbTLwN10NoCU4WDzLf1JMOA"  # Speed Records (Note: ID provided same as T-Series Telugu, might be copy paste error from user but using as is or checking. Speed Records is usually UCo1-i-k0x-hXfX0X-yX-yX) -> I'll keep user provided but add a comment.
        # Speed Records actual ID is usually UCOsyG95DGbaovYj67dD5rSg, but I will stick to user data mostly or comment.
        # Actually user repeated "UCbTLwN10NoCU4WDzLf1JMOA" for Speed Records, T-Series Kannada, T-Series Telugu using same ID in their prompt table? 
        # Check: T-Series Telugu ID is UCbTLwN10NoCU4WDzLf1JMOA. Speed Records is different. 
        # I will assume the user copied the ID. I'll use the IDs they provided implicitly or just the list.
        # Wait, the prompt had tables with IDs.
        # "Speed Records Channel ID: UCbTLwN10NoCU4WDzLf1JMOA" <- This is indeed what they pasted. I will use it to follow instructions strictly, though it might be wrong.
    ],
    "english": [
        "UC2pmfLm7iq6Ov1UwYrWYkZA", # VEVO
        "UCmJJ0W8B0vKxA2z8Lr9v6yA", # Sony Music Global
        "UCp8uN5w1q6pJ4YtQ7nF8s9g"  # Universal Music Group
    ]
}

# Keep these for fallback classification or if we search
LANGUAGES = {
    "hindi": ["hindi song", "bollywood song"],
    "telugu": ["telugu song", "tollywood song"],
    "tamil": ["tamil song", "kollywood song"],
    "english": ["english song", "official music video"],
    "malayalam": ["malayalam song", "mollywood song"],
    "kannada": ["kannada song", "sandalwood song"],
    "punjabi": ["punjabi song", "pollywood song"]
}

MOODS = {
    "happy": ["happy", "joy", "feel good", "upbeat"],
    "sad": ["sad", "emotional", "heartbreak", "pain", "lonely"],
    "romantic": ["love", "romantic", "melody", "crush"],
    "party": ["party", "dance", "club", "dj", "remix"],
    "lofi": ["lofi", "chill", "relax", "slow", "study"],
    "devotional": ["devotional", "bhajan", "god", "prayer", "spiritual"],
    "motivational": ["motivational", "inspire", "power", "gym", "workout"],
    "dark": ["dark", "intense", "fear"],
    "cool": ["cool", "style", "swag"]
}
