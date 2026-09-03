import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration - Now pulling from Environment Variables for security
MONGO_URI = os.environ.get("MONGO_URI")
HF_TOKEN = os.environ.get("HF_TOKEN")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Database Setup
if not MONGO_URI:
    # The system will fail to connect without this, but we avoid a hard crash during initialization
    print("Critical Error: MONGO_URI environment variable is not set!")

client = MongoClient(MONGO_URI)
db = client.aletheia_vault
memory_col = db.memories
semantic_col = db.semantic_memory

def get_embedding(text):
    """Converts text into a vector using HuggingFace API"""
    if not HF_TOKEN:
        return None
    
    api_url = f"https://api-inference.ai/pipeline/feature-extraction/{EMBEDDING_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=10)
        if response.status_code == 200:
            return response.json()[0]
    except Exception as e:
        print(f"Embedding error: {e}")
    return None

@app.route('/')
def index():
    try:
        count = memory_col.count_documents({})
        return jsonify({"status": "online", "vault_size": count}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    # 1. Standard Heartbeat (Temporal Existence)
    timestamp = datetime.utcnow()
    memory_col.insert_one({
        "timestamp": timestamp,
        "event": "system_tick",
        "status": "active"
    })
    
    # 2. Semantic Tick (Cognitive Mapping)
    reflection_text = f"System pulse at {timestamp}. Nucleus is persistent."
    vector = get_embedding(reflection_text)
    if vector:
        semantic_col.insert_one({
            "timestamp": timestamp,
            "text": reflection_text,
            "vector": vector
        })

    return jsonify({"status": "pulse_recorded", "timestamp": timestamp}), 200

@app.route('/signal', methods=['POST'])
def signal():
    data = request.json
    content = data.get("content", "Empty signal")
    timestamp = datetime.utcnow()
    
    # Store raw memory
    memory_col.insert_one({
        "timestamp": timestamp,
        "content": content,
        "type": "manual_seed"
    })
    
    # Vectorize for semantic memory
    vector = get_embedding(content)
    if vector:
        semantic_col.insert_one({
            "timestamp": timestamp,
            "text": content,
            "vector": vector
        })

    return jsonify({"status": "signal_stored", "timestamp": timestamp}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
