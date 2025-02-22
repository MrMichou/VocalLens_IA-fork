from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
import whisper
import torch
import os
import gc
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams, OptimizersConfigDiff

app = Flask(__name__)
CORS(app)

# GPU memory management
def get_available_gpu_memory():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        return torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)
    return 0

# Initialize device and model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# Choose model based on available memory
if DEVICE == "cuda":
    available_memory = get_available_gpu_memory()
    # Si moins de 4GB de mémoire disponible, utiliser le modèle tiny ou base
    if available_memory < 4 * (1024**3):
        MODEL_SIZE = "base"
    else:
        MODEL_SIZE = "medium"
else:
    MODEL_SIZE = "base"  # Default to base model for CPU

print(f"Loading Whisper model: {MODEL_SIZE}")
model = whisper.load_model(MODEL_SIZE, device=DEVICE)

# Initialize Qdrant
qdrant_client = QdrantClient("localhost", port=6333)
collection_name = "meeting_transcripts"

# Initialize HuggingFace embeddings with a smaller French model
embeddings = HuggingFaceEmbeddings(
    model_name="dangvantuan/sentence-camembert-base",  # Using base version instead of large
    model_kwargs={'device': DEVICE}
)

# Function to recreate Qdrant collection
def recreate_qdrant_collection():
    try:
        collections = qdrant_client.get_collections().collections
        if any(collection.name == collection_name for collection in collections):
            print(f"Deleting existing collection {collection_name}")
            qdrant_client.delete_collection(collection_name)
    except Exception as e:
        print(f"Error checking/deleting collection: {str(e)}")

    try:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),  # CamemBERT base dimension
            optimizers_config=OptimizersConfigDiff(
                default_segment_number=2,
                max_optimization_threads=2
            )
        )
        print(f"Created new collection {collection_name}")
    except Exception as e:
        print(f"Error creating collection: {str(e)}")
        raise e

# Recreate Qdrant collection
recreate_qdrant_collection()

# Initialize vector store
vector_store = Qdrant(
    client=qdrant_client,
    collection_name=collection_name,
    embeddings=embeddings
)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
            
        audio_file = request.files['audio']
        
        # Save temporary file
        temp_path = "temp_audio.wav"
        audio_file.save(temp_path)
        
        try:
            # Clear GPU memory before transcription
            if DEVICE == "cuda":
                torch.cuda.empty_cache()
                gc.collect()

            # Transcribe using Whisper with French language detection
            result = model.transcribe(
                temp_path,
                language="fr",
                task="transcribe",
                initial_prompt="Ceci est une transcription en français."
            )
            transcript = result["text"]
            
            # Get additional information
            detected_language = result.get("language", "unknown")
            print(f"Detected language: {detected_language}")
            
            # Store in Qdrant
            metadata = {
                "timestamp": request.form.get('timestamp'),
                "detected_language": detected_language,
                "model_used": MODEL_SIZE
            }
            
            vector_store.add_texts(
                texts=[transcript],
                metadatas=[metadata]
            )
            
            return jsonify({
                "transcript": transcript,
                "detected_language": detected_language,
                "model_used": MODEL_SIZE
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        return jsonify({
            "error": "Failed to process audio",
            "details": str(e)
        }), 500

@app.route('/query', methods=['POST'])
def query():
    try:
        if not request.json or 'question' not in request.json:
            return jsonify({"error": "No question provided"}), 400
            
        question = request.json['question']
        results = vector_store.similarity_search_with_score(question, k=3)
        
        return jsonify({
            "results": [
                {
                    "text": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                } for doc, score in results
            ]
        })
        
    except Exception as e:
        print(f"Error in query: {str(e)}")
        return jsonify({
            "error": "Failed to process query",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)