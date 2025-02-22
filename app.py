from flask import Flask, request
from flask_cors import CORS
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
import openai
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def init_qdrant():
    """Initialize Qdrant client and collection with proper error handling"""
    client = QdrantClient("localhost", port=6333)
    collection_name = "meeting_transcripts"
    
    try:
        # Check if collection exists
        collections = client.get_collections()
        collection_exists = any(col.name == collection_name for col in collections.collections)
        
        if not collection_exists:
            logger.info(f"Creating new collection: {collection_name}")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                optimizers_config={
                    "default_segment_number": 2,
                    "max_optimization_threads": 2
                }
            )
        else:
            logger.info(f"Collection {collection_name} already exists")
            
        return client, collection_name
        
    except Exception as e:
        logger.error(f"Error initializing Qdrant: {str(e)}")
        raise

# Initialize clients
try:
    client, collection_name = init_qdrant()
    embeddings = OpenAIEmbeddings()
    vector_store = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings
    )
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return {"error": "No audio file provided"}, 400
            
        audio_file = request.files['audio']
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
        # Store in Qdrant
        vector_store.add_texts(
            texts=[transcript['text']],
            metadatas=[{"timestamp": request.form.get('timestamp')}]
        )
        return {"transcript": transcript['text']}
        
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {str(e)}")
        return {"error": str(e)}, 500

@app.route('/query', methods=['POST'])
def query():
    try:
        if not request.json or 'question' not in request.json:
            return {"error": "No question provided"}, 400
            
        question = request.json['question']
        results = vector_store.similarity_search_with_score(question, k=3)
        return {
            "results": [
                {
                    "text": doc.page_content,
                    "score": float(score),  # Convert to float for JSON serialization
                    "metadata": doc.metadata
                } for doc, score in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in query endpoint: {str(e)}")
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)