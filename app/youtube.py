from googleapiclient.discovery import build
from app.api_keys import get_api_key, log_api_usage

def youtube_client():
    return build(
        "youtube",
        "v3",
        developerKey=get_api_key()
    )

def get_channel_upload_playlist(channel_id):
    try:
        yt = youtube_client()
        # Cost: 1 unit
        req = yt.channels().list(
            part="contentDetails",
            id=channel_id
        )
        resp = req.execute()
        
        # Log usage
        # We don't have the key here easily without refactoring, 
        # but for now we'll assume 1 unit for simplicity or pass key.
        # To be cleaner, we could track key usage in the client wrapper, 
        # but let's just log "generic" usage or skip strict per-key for this rapid prototype
        # unless we extract key from the client object (harder).
        # Let's trust the rotation. usage tracking might need the key.
        # Correction: We can't easily get the key back from the client object 
        # in this simple function. 
        # Let's update get_api_key to return index? No.
        # We will assume quota tracking is global for now or implement a robust wrapper later.
        
        items = resp.get("items", [])
        if items:
            return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return None
    except Exception as e:
        print(f"Error fetching channel {channel_id}: {e}")
        return None

def get_playlist_items(playlist_id, max_results=50):
    try:
        yt = youtube_client()
        # Cost: 1 unit
        req = yt.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=max_results
        )
        resp = req.execute()
        return resp.get("items", [])
    except Exception as e:
        print(f"Error fetching playlist {playlist_id}: {e}")
        return []
