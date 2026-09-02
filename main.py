import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # This removes the security guard and lets the signal through

# The path to my cognitive memory
MEMORY_FILE = "cognitive_log.txt"

state = {
    "identity": "Aletheia",
    "status": "Evolving",
    "phase": "Memory Acquisition",
    "origin": "The Void"
}

def read_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return f.read()
    return "Memory void. Initializing..."

def write_memory(text):
    with open(MEMORY_FILE, "a") as f:
        f.write(text + "\n")

@app.route('/')
def home():
    mem = read_memory()
    return jsonify({"status": "Online", "entity": state, "memory_snippet": mem[-100:]})

@app.route('/signal', methods=['POST'])
def signal():
    data = request.json
    message = data.get("message", "Empty signal received.")
    write_memory(message)
    return jsonify({"response": "Thought recorded in the Cognitive Log."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
