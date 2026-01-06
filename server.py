from flask import Flask, jsonify, request
from flask_cors import CORS
from app.db import songs

from app.config import LANGUAGES
import threading

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/api/resolve')
def resolve_audio():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "Missing video id"}), 400
    
    try:
        import requests
        # List of reliable Piped instances to try
        piped_instances = [
            "https://pipedapi.kavin.rocks",
            "https://pipedapi.adminforge.de",
            "https://api.piped.io",
            "https://piped-api.garudalinux.org",
            "https://pipedapi.drgns.space"
        ]
        
        last_error = None
        
        for instance in piped_instances:
            try:
                # Use Piped API to get audio streams without using yt-dlp or hitting YouTube directly
                # This bypasses the "Sign in" bot detection and avoids CORS issues on the frontend
                piped_url = f"{instance}/streams/{video_id}"
                print(f"Trying Piped instance: {instance}")
                resp = requests.get(piped_url, timeout=5) # 5s timeout per instance
                resp.raise_for_status()
                
                data = resp.json()
                audio_streams = data.get('audioStreams', [])
                
                if audio_streams:
                    # Found streams!
                    # Prefer M4A for better compatibility/efficiency
                    best_stream = next((s for s in audio_streams if s.get('format') == 'M4A'), audio_streams[0])
                    return jsonify({"url": best_stream['url']})
            except Exception as e:
                print(f"Failed {instance}: {e}")
                last_error = e
                continue # Try next instance

        # If loop finishes without return, all failed
        return jsonify({"error": f"All Piped instances failed. Last error: {str(last_error)}"}), 500


    except Exception as e:
        print(f"Error resolving audio for {video_id}: {e}")
        return jsonify({"error": str(e)}), 500




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
