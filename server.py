from flask import Flask, jsonify, request
from app.db import songs
from app.collector import collect
from app.config import LANGUAGES
import threading

app = Flask(__name__)

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
    results = list(songs.find(query, {"_id": 0}).skip(skip).limit(limit))
    
    return jsonify({
        "count": len(results),
        "page": page,
        "results": results
    })

def run_collection_task():
    print("Starting background collection...")
    for lang, queries in LANGUAGES.items():
        for q in queries:
            collect(q)
    print("Background collection finished.")

@app.route('/api/trigger-collect', methods=['POST'])
def trigger_collect():
    # Run in background thread to avoid blocking response
    thread = threading.Thread(target=run_collection_task)
    thread.start()
    return jsonify({"message": "Collection task started in background"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
