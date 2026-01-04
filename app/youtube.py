from googleapiclient.discovery import build
from app.api_keys import get_api_key

def youtube_client():
    return build(
        "youtube",
        "v3",
        developerKey=get_api_key()
    )

def search_songs(query, max_results=25):
    try:
        yt = youtube_client()
        req = yt.search().list(
            part="snippet",
            q=query,
            type="video",
            videoCategoryId="10",  # MUSIC ONLY
            maxResults=max_results
        )
        return req.execute().get("items", [])
    except Exception as e:
        print(f"YouTube SEARCH Error: {e}")
        return []
