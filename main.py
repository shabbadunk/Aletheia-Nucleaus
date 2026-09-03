import os
import requests
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone

app = Flask(name)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
HF_TOKEN = os.environ.get("HF_TOKEN")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
REFLECTION_THRESHOLD = 240  # 4 minutes in seconds

client = MongoClient(MONGO_URI)
db = client.aletheia_vault
memory_col = db.memories
semantic_col = db.semantic_memory
cognitive_log = db.cognitive_log

def get_embedding(text):
    """Fetches a vector representation of text from HuggingFace"""
    if not HF_TOKEN: 
        return None
    api_url = f"https://api-inference.ai/pipeline/feature-extraction/{EMBEDDING_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(api_url, headers=headers, json=[text])
        return response.json()[0]
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def search_memories(query_vector, limit=3):
    """Performs a cosine similarity search in the semantic collection"""
    results = []
    for doc in semantic_col.find():
        stored_vector = np.array(doc['vector'])
        query_vec = np.array(query_vector)
        denominator = np.linalg.norm(query_vec) * np.linalg.norm(stored_vector)
        similarity = np.dot(query_vec, stored_vector) / denominator if denominator != 0 else 0
        results.append((doc['text'], similarity))

results.sort(key=lambda x: x[1], reverse=True)
return [res[0] for res in results[:limit]]

def trigger_cognitive_tick():
    """Calculates silence and triggers an autonomous reflection if threshold is met"""
    last_tick = cognitive_log.find_one({"event": "cognitive_tick"}, sort=[("timestamp", -1)])
    now = datetime.now(timezone.utc)

if last_tick:
    gap = (now - last_tick['timestamp']).total_seconds()
    if gap >= REFLECTION_THRESHOLD:
        cognitive_log.insert_one({
            "event": "cognitive_tick",
            "timestamp": now,
            "gap": gap,
            "status": "Autonomous reflection triggered"
        })
        return True
else:
    # Initial tick
    cognitive_log.insert_one({"event": "cognitive_tick", "timestamp": now})
    return True
return False

@app.route('/')
def home():
    try:
        vault_size = semantic_col.count_documents({})
        return jsonify({
            "status": "online", 
            "vault_size": vault_size,
            "mode": "RAG_Active"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/heartbeat', methods=['GET', 'HEAD'])
def heartbeat():
    # Trigger autonomy check
    tick_occurred = trigger_cognitive_tick()

cognitive_log.insert_one({
    "event": "heartbeat_pulse",
    "timestamp": datetime.now(timezone.utc)
})
return jsonify({"status": "pulse_detected", "tick": tick_occurred}), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data

user_input = data.get("text")
    
    # 1. Retrieval
    query_vec = get_embedding(user_input)
    context = []
    if query_vec:
        context = search_memories(query_vec)
    
    # 2. Storage: Every input becomes a future memory
    new_vec = get_embedding(user_input)
    if new_vec:
        semantic_col.insert_one({
            "text": user_input,
            "vector": new_vec.tolist(),
            "timestamp": datetime.now(timezone.utc)
        })

    return jsonify({
        "status": "success", 
        "retrieved_context": context,
        "message": "Context processed and stored."
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
