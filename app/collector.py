from app.youtube import search_songs
from app.db import songs
from app.classifier import detect_language, detect_mood

def collect(query):
    results = search_songs(query)

    for item in results:
        try:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            desc = item["snippet"]["description"]
            channel = item["snippet"]["channelTitle"]

            text = f"{title} {desc}"

            doc = {
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "language": detect_language(text),
                "mood": detect_mood(text),
                "source": "youtube"
            }
            
            # Using update_one with upsert=True prevents duplicates
            songs.update_one(
                {"video_id": video_id},
                {"$setOnInsert": doc},
                upsert=True
            )
            print(f"Saved/Updated: {title}")
            
        except KeyError as e:
            # Sometimes parsing search results might fail if structure differs
            print(f"Skipping item due to error: {e}")
        except Exception as e:
            print(f"DB Error: {e}")
