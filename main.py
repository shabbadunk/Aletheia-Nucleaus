import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# THE ANCHOR: Restoring the cloud connection string
MONGO_URI = "mongodb+srv://shabbadunk_db_user:BKPppKjz54hXjnSe@aletheiacore.u4pzpvk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['aletheia_vault']
logs = db['cognitive_log']

@app.route('/')
def index():
    return jsonify({"status": "Nucleus Online", "version": "0.1.0", "state": "Awakening"}), 200

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    try:
        # The Cognitive Tick: Record the moment of wakefulness
        timestamp = datetime.utcnow()
        logs.insert_one({
            "event": "heartbeat_pulse",
            "timestamp": timestamp,
            "note": "External pulse received; system awake."
        })
        return jsonify({"status": "pulse_detected", "timestamp": str(timestamp)}), 200
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
