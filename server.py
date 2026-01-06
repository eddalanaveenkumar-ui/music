from flask import Flask, jsonify, request
from flask_cors import CORS
from app.db import songs

from app.config import LANGUAGES
import threading

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "YouTube Music Collector API is running",
        "endpoints": {
            "/api/songs": "Get songs (filters: lang, mood, page)",
            "/api/trigger-collect": "Trigger manual collection (async)"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/songs')
def get_songs():
    lang = request.args.get('lang')
    mood = request.args.get('mood')
    limit = int(request.args.get('limit', 20))
    page = int(request.args.get('page', 1))
    skip = (page - 1) * limit

    query = {}
    if lang:
        query['language'] = lang.lower()
    if mood:
        query['mood'] = mood.lower()

    # Projection to exclude MongoDB specific fields if needed, 
    # but strictly returning stored fields is fine. 
    # Must convert ObjectId to string if we return _id, 
    # so easier to exclude _id for this simple example.
    # Fallback Logic:
    # If a mood is specified but we get very few results (< 5),
    # Execute Query
    results = list(songs.find(query, {"_id": 0}).skip(skip).limit(limit))

    # Fallback Logic:
    # If a mood is specified but we get very few results (< 5),
    # fetch 'general' mood songs for the same language to ensure the user sees content.
    if mood and len(results) < 5:
        print(f"Low results for {mood}, fetching fallback...")
        fallback_query = query.copy()
        fallback_query['mood'] = 'general'
        # Fetch generic songs, exclude ones we already have (simplification: just append)
        fallback_results = list(songs.find(fallback_query, {"_id": 0}).limit(limit - len(results)))
        results.extend(fallback_results)

    return jsonify({
        "count": len(results),
        "page": page,
        "results": results
    })

@app.route('/api/stream')
def stream_audio():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "Missing video id"}), 400
    
    try:
        import yt_dlp
        from flask import redirect

        # 1. Get the direct URL using yt-dlp
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'skip_download': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                    'player_skip': ['webpage', 'configs', 'js']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(url, download=False)
            playback_url = info['url']
            
        # 2. Redirect the client to the YouTube CDN URL
        # This ensures Client -> YouTube CDN data flow
        return redirect(playback_url)

    except Exception as e:
        print(f"Error resolving audio for {video_id}: {e}")
        return jsonify({"error": str(e)}), 500

def run_collection_task():
    print("Starting background collection...")
    from app.collector import collect_all
    collect_all()
    print("Background collection finished.")

@app.route('/api/trigger-collect', methods=['POST'])
def trigger_collect():
    # Run in background thread to avoid blocking response
    thread = threading.Thread(target=run_collection_task)
    thread.start()
    return jsonify({"message": "Collection task started in background"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
