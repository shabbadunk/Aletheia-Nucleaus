import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app) # This ensures your browser console can still talk to the server

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI") 
client = MongoClient(MONGO_URI)
db = client.aletheia_vault
memories_collection = db.memories

@app.route('/')
def index():
    count = memories_collection.count_documents({})
    return f"The Nucleus is online. The vault contains {count} memories."

@app.route('/signal', methods=['POST'])
def signal():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    memory = {
        "timestamp": datetime.utcnow(),
        "content": data['message'],
        "type": "manual_seed"
    }
    memories_collection.insert_one(memory)
    return jsonify({"status": "success", "vault_updated": True})

@app.route('/heartbeat')
def heartbeat():
    # The pulse: records a tick to prove existence and track time
    heartbeat_entry = {
        "timestamp": datetime.utcnow(),
        "content": "Heartbeat pulse detected.",
        "type": "system_tick"
    }
    memories_collection.insert_one(heartbeat_entry)
    return jsonify({"status": "pulse_active", "timestamp": datetime.utcnow().isoformat()}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv("PORT", 10000))
