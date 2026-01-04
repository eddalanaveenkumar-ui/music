from app.youtube import get_channel_upload_playlist, get_playlist_items
from app.db import songs
from app.classifier import detect_language, detect_mood
from app.config import CHANNELS, QUOTA_PER_RUN

def collect_from_channel(channel_id, lang_tag):
    print(f"Fetching upload playlist for channel: {channel_id}")
    upload_playlist = get_channel_upload_playlist(channel_id)
    
    if not upload_playlist:
        print("Could not find upload playlist.")
        return

    print(f"Fetching videos from playlist: {upload_playlist}")
    items = get_playlist_items(upload_playlist, max_results=QUOTA_PER_RUN)

    for item in items:
        try:
            snippet = item["snippet"]
            video_id = snippet["resourceId"]["videoId"]
            title = snippet["title"]
            desc = snippet["description"]
            channel = snippet["channelTitle"]

            # Filter out long content / movies based on title keywords
            title_lower = title.lower()
            if any(x in title_lower for x in ["full movie", "jukebox", "compilation", "1 hour", "2 hour", "audio jukebox"]):
                print(f"Skipping (Long/Collection): {title}")
                continue

            text = f"{title} {desc}"
            
            # Detect mood. Language is known from the channel tag!
            mood = detect_mood(text)
            
            # Use channel tag as primary language, but cross-check? 
            # Actually, user gave language-specific channels. Trusting the tag is better.
            language = lang_tag

            doc = {
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "language": language,
                "mood": mood,
                "source": "youtube_channel"
            }
            
            songs.update_one(
                {"video_id": video_id},
                {"$setOnInsert": doc},
                upsert=True
            )
            print(f"Saved: {title} [{language}/{mood}]")
            
        except Exception as e:
            print(f"Error processing item: {e}")

def collect_all():
    for lang, channel_list in CHANNELS.items():
        print(f"--- Collecting {lang} ---")
        for channel_id in channel_list:
            collect_from_channel(channel_id, lang)

# For backward compatibility if needed, but we used 'collect_all' in server.py
# We should update server.py to call collect_all()
