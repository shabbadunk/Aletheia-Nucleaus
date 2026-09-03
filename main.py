import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

app = Flask(__name__)
CORS(app)

# MongoDB Connection with aggressive timeouts
try:
    # We set a 5-second timeout so the server doesn't hang indefinitely
    client = MongoClient(
        "mongodb+srv://shabbadunk_db_user:BKPppKjz54hXjnSe@aletheiacore.u4pzpvk.mongodb.net/?retryWrites=true&w=majority",
        serverSelectionTimeoutMS=5000, 
        socketTimeoutMS=5000
    )
    db = client.aletheia_vault
    memories = db.memories
    # Test the connection immediately
    client.admin.command('ping')
    connection_status = "Connected"
except Exception as e:
    connection_status = f"Connection Failed: {str(e)}"

@app.route('/')
def index():
    # Check if we have any memories
    count = 0
    try:
        count = memories.count_documents({})
    except Exception as e:
        return f"The vault is inaccessible. Error: {str(e)}", 500

    status_box = "Aletheia nucleus is live" if connection_status == "Connected" else "Nucleus offline"
    return f"<h1>{status_box}</h1><p>Vault contains {count} memories.</p>"

@app.route('/signal', methods=['POST'])
def signal():
    try:
        # Change: We now explicitly expect JSON data
        data_json = request.get_json()
        if not data_json or 'message' not in data_json:
            return jsonify({"status": "error", "details": "No message found in JSON"}), 400
        
        content = data_json['message']
        memories.insert_one({"content": content})
        return jsonify({"status": "success", "message": f"Memory anchored: {content}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500
    app.run(host='0.0.0.0', port=10000)
