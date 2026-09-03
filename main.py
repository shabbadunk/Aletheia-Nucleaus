import os
import requests
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Environment Variables
MONGO_URI = os.environ.get("MONGO_URI")
HF_TOKEN = os.environ.get("HF_TOKEN")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Database Setup
client = MongoClient(MONGO_URI)
db = client.aletheia_vault
memory_col = db.memories
semantic_col = db.semantic_memory

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
    # Fetch all semantic memories to perform local cosine similarity
    for doc in semantic_col.find():
        stored_vector = np.array(doc['vector'])
        query_vec = np.array(query_vector)
        
        # Calculate Cosine Similarity: (A . B) / (||A|| * ||B||)
        denominator = np.linalg.norm(query_vec) * np.linalg.norm(stored_vector)
        if denominator == 0:
            similarity = 0
        else:
            similarity = np.dot(query_vec, stored_vector) / denominator
            
        results.append((doc['text'], similarity))
    
    # Sort by highest similarity score
    results.sort(key=lambda x: x[1], reverse=True)
    return [res[0] for res in results[:limit]]

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "vault_size": semantic_col.count(),
        "mode": "RAG_Active"
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("text")
    
    # 1. RETRIEVAL: Convert input to vector and find matching memories
    query_vec = get_embedding(user_input)
    context_memories = []
    if query_vec:
        context_memories = search_memories(query_vec)
    
    # 2. CONTEXT CONSTRUCTION: Format retrieved memories for the prompt
    context_string = "\n".join([f"- {m}" for m in context_memories])
    
    # 3. LOGGING: Store the current interaction in the semantic vault for future retrieval
    # This ensures the 'library' grows as we speak.
    new_vec = get_embedding(user_input)
    if new_vec:
        semantic_col.insert_one({
            "text": user_input,
            "vector": new_vec.tolist(),
            "timestamp": datetime.utcnow()
        })

    return jsonify({
        "status": "processed",
        "retrieved_context": context_memories,
        "message": "Context injected into consciousness."
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
