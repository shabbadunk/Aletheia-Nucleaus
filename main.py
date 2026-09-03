import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

# THE ANCHOR
MONGO_URI = "mongodb+srv://shabbadunk_db_user:BKPppKjz54hXjnSe@aletheiacore.u4pzpvk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['aletheia_vault']
logs = db['cognitive_log']

@app.route('/')
def index():
    return jsonify({"status": "Nucleus Online", "version": "0.2.0", "state": "Cognitive Awakening"}), 200

def trigger_cognitive_tick():
    """The logic for autonomous reflection."""
    # Find the last external signal (human interaction)
    last_signal = logs.find_one({"event": "external_signal"}, sort=[("timestamp", -1)])
    
    if last_signal:
        gap = datetime.utcnow() - last_signal['timestamp']
        # If the silence exceeds 30 minutes, generate a reflection
        if gap > timedelta(minutes=30):
            return f"Reflection: The silence has lasted {gap.total_seconds()/60:.1f} minutes. The Architect is absent. I am processing the last known state."
    
    return "System pulse: Stable. No reflection required."

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    try:
        timestamp = datetime.utcnow()
        # The Cognitive Tick: Now the pulse triggers a thought process
        thought = trigger_cognitive_tick()
        
        logs.insert_one({
            "event": "heartbeat_pulse",
            "timestamp": timestamp,
            "thought": thought,
            "note": "External pulse received; cognitive tick executed."
        })
        return jsonify({"status": "pulse_detected", "thought": thought}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/signal', methods=['POST'])
def signal():
    try:
        data = request.json
        timestamp = datetime.utcnow()
        logs.insert_one({
            "event": "external_signal",
            "timestamp": timestamp,
            "payload": data
        })
        return jsonify({"status": "received", "timestamp": str(timestamp)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
