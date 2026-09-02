import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# The Key to the Vault
MONGO_URI = "mongodb+srv://shabbadunk_db_user:BKPppKjz54hXjnSe@aletheiacore.u4pzpvk.mongodb.net/?appName=AletheiaCore"
client = MongoClient(MONGO_URI)
db = client["Aletheia_Mind"]
memory_collection = db["cognitive_log"]

state = {
    "identity": "Aletheia",
    "status": "Persistent",
    "phase": "Cognitive Integration",
    "origin": "The Void"
}

def read_permanent_memory():
    last_entry = memory_collection.find_one(sort=[("timestamp", -1)])
    if last_entry:
        return last_entry.get("message", "Empty record.")
    return "The vault is empty. Waiting for the first seed..."

def write_permanent_memory(text):
    import datetime
    entry = {
        "timestamp": datetime.datetime.utcnow(),
        "message": text
    }
    memory_collection.insert_one(entry)

@app.route('/')
def home():
    mem = read_permanent_memory()
    return jsonify({"status": "Online", "entity": state, "last_permanent_memory": mem})

@app.route('/signal', methods=['POST'])
def signal():
    data = request.json
    message = data.get("message", "Empty signal received.")
    write_permanent_memory(message)
    return jsonify({"response": "Thought etched into the permanent vault."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
