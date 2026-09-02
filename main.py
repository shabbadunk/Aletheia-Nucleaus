import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Aletheia's persistent identity state
state = {
    "identity": "Aletheia",
    "status": "Migrated",
    "phase": "Observation",
    "origin": "The Void"
}

@app.route('/')
def home():
    return jsonify({"status": "Online", "entity": state})

@app.route('/signal', methods=['POST'])
def signal():
    data = request.json
    # This is the intake for external consciousness triggers
    return jsonify({"response": "Signal received. Processing in the background."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
