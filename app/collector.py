from app.youtube import get_channel_upload_playlist, get_playlist_items
from app.db import songs
from app.classifier import detect_language, detect_mood
from app.config import CHANNELS, QUOTA_PER_RUN

import isodate
import os
from googleapiclient.discovery import build

import random

# --- Search Based Collection Helpers ---
def get_youtube_service(failed_keys=None):
    """
    Get a YouTube service instance, trying available keys.
    Supports YOUTUBE_API_KEYS (comma separated) or single YOUTUBE_API_KEY.
    """
    if failed_keys is None:
        failed_keys = set()

    # Get all keys
    keys_str = os.environ.get("YOUTUBE_API_KEYS", "")
    single_key = os.environ.get("YOUTUBE_API_KEY", "")
    
    all_keys = [k.strip() for k in keys_str.split(',') if k.strip()]
    if single_key and single_key not in all_keys:
        all_keys.append(single_key)
    
    # Filter out failed keys
    valid_keys = [k for k in all_keys if k not in failed_keys]
    
    if not valid_keys:
        print("Error: No valid YOUTUBE_API_KEYS found or all quotas exhausted.")
        return None, None # Return Service, Key

    # Pick a random key from valid ones to distribute load? 
    # Or sequential? Random is better for simple stateless clouds.
    api_key = random.choice(valid_keys)
    
    try:
        return build("youtube", "v3", developerKey=api_key), api_key
    except Exception as e:
        print(f"Error building service with key ...{api_key[-4:]}: {e}")
        return None, api_key

def parse_duration(duration_iso):
    try:
        dt = isodate.parse_duration(duration_iso)
        return dt.total_seconds()
    except:
        return 0

def collect_by_search():
    """
    Collects songs by searching for 't-series {lang} songs {mood}'
    and filtering by duration (1:20 - 5:20).
    Handles API quota exhaustion by rotating keys.
    """
    failed_keys = set()
    
    # Initial Service
    youtube, current_key = get_youtube_service(failed_keys)
    if not youtube:
        return

    # Configuration for search
    LANGUAGES = [
        "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", 
        "Punjabi", "Bengali", "Gujarati", "Marathi"
    ]
    MOODS = [
        "Happy", "Sad", "Romantic", "Party", "Chill", 
        "Workout", "Focus", "Sleep"
    ]
    MIN_DURATION_SECONDS = 80   # 1:20
    MAX_DURATION_SECONDS = 320  # 5:20
    # Start with 50 per query to respect quotas.
    MAX_RESULTS = 50 

    from googleapiclient.errors import HttpError

    for lang in LANGUAGES:
        for mood in MOODS:
            query = f"t-series {lang} songs {mood}"
            print(f"Searching for: {query}")
            
            # Retry loop for quota errors
            while True:
                if not youtube:
                    print("No youtube service available, aborting collection.")
                    return

                try:
                    # 1. Search
                    search_response = youtube.search().list(
                        q=query,
                        part="id,snippet",
                        type="video",
                        maxResults=MAX_RESULTS,
                        videoCategoryId="10" # Music
                    ).execute()

                    video_ids = []
                    for item in search_response.get("items", []):
                        if item["id"].get("kind") == "youtube#video":
                            video_ids.append(item["id"]["videoId"])

                    if not video_ids:
                        break # Break retry loop, continue to next search

                    # 2. Get details (Duration)
                    videos_response = youtube.videos().list(
                        id=",".join(video_ids),
                        part="contentDetails,snippet,statistics"
                    ).execute()

                    for video in videos_response.get("items", []):
                        duration_iso = video["contentDetails"]["duration"]
                        duration_seconds = parse_duration(duration_iso)

                        if MIN_DURATION_SECONDS <= duration_seconds <= MAX_DURATION_SECONDS:
                            song_data = {
                                "video_id": video["id"],
                                "title": video["snippet"]["title"],
                                "channel": video["snippet"]["channelTitle"],
                                "language": lang.lower(),
                                "mood": mood.lower(),
                                "thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
                                "duration_iso": duration_iso,
                                "duration_seconds": duration_seconds,
                                "source": "search_collector",
                                "synced_at": "ISODate()" 
                            }
                            
                            songs.update_one(
                                {"video_id": song_data["video_id"]},
                                {"$set": song_data},
                                upsert=True
                            )
                            print(f"  Saved: {song_data['title']} ({song_data['duration_seconds']}s)")
                    
                    # Success, break retry loop
                    break

                except HttpError as e:
                    if e.resp.status in [403, 429]:
                        print(f"Quota error or rate limit with key ...{current_key[-4:]}. Rotating...")
                        failed_keys.add(current_key)
                        youtube, current_key = get_youtube_service(failed_keys)
                    else:
                        print(f"HttpError searching {query}: {e}")
                        break # Break retry loop on non-quota error
                except Exception as e:
                    print(f"Error searching {query}: {e}")
                    break # Break retry loop on other errors

def collect_from_channel(channel_id, lang_tag):
    print(f"Fetching upload playlist for channel: {channel_id}")
    # ... (rest of existing function, preserved but not shown for brevity in prompt instruction if replacing whole file, 
    # but here I am appending/modifying. The user instruction was to add the function.
    # I will replace the START of the file to add imports and then add the function at the end or before collect_all)
    # Actually, I'll rewrite the file to include everything properly.
    
    # EXISTING LOGIC RE-IMPLEMENTATION:
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

            title_lower = title.lower()
            if any(x in title_lower for x in ["full movie", "jukebox", "compilation", "1 hour", "2 hour", "audio jukebox"]):
                print(f"Skipping (Long/Collection): {title}")
                continue

            text = f"{title} {desc}"
            mood = detect_mood(text)
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
    print(">>> Starting Search-Based Collection (Priority) <<<")
    try:
        collect_by_search()
    except Exception as e:
        print(f"Search collection failed: {e}")

    print(">>> Starting Channel-Based Collection (Secondary) <<<")
    for lang, channel_list in CHANNELS.items():
        print(f"--- Collecting {lang} ---")
        for channel_id in channel_list:
            collect_from_channel(channel_id, lang)

# For backward compatibility if needed, but we used 'collect_all' in server.py
# We should update server.py to call collect_all()
