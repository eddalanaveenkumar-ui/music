from app.config import LANGUAGES, MOODS

def detect_language(text):
    text = text.lower()
    for lang, keys in LANGUAGES.items():
        if any(k in text for k in keys):
            return lang
    return "unknown"

def detect_mood(text):
    text = text.lower()
    for mood, keys in MOODS.items():
        if any(k in text for k in keys):
            return mood
    return "general"
