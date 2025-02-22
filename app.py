from flask import Flask, request
from flask_cors import CORS
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
import openai
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

app = Flask(__name__)
CORS(app)

# Initialize Qdrant
client = QdrantClient("localhost", port=6333)
collection_name = "meeting_transcripts"

# Create collection if it doesn't exist
try:
    collections = client.get_collections()
    exists = any(col.name == collection_name for col in collections.collections)
    
    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1536,  # OpenAI embeddings dimension
                distance=models.Distance.COSINE
            )
        )
        print(f"Collection {collection_name} created successfully")
    else:
        print(f"Collection {collection_name} already exists")

except Exception as e:
    print(f"Error with Qdrant setup: {str(e)}")
    raise

embeddings = OpenAIEmbeddings()
vector_store = Qdrant(
    client=client,
    collection_name=collection_name,
    embeddings=embeddings
)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    print("Received transcribe request")  # Debug log
    print("Files:", request.files)  # Debug log
    audio_file = request.files['audio']
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print("Transcript:", transcript)  # Debug log
    
    # Store in Qdrant
    vector_store.add_texts(
        texts=[transcript['text']],
        metadatas=[{"timestamp": request.form.get('timestamp')}]
    )
    return {"transcript": transcript['text']}

@app.route('/query', methods=['POST'])
def query():
    print("Received query request")  # Debug log
    print("Data:", request.json)  # Debug log
    question = request.json['question']
    results = vector_store.similarity_search_with_score(question, k=3)
    print("Results:", results)  # Debug log
    return {"results": [{"text": doc.page_content, "score": score} for doc, score in results]}

if __name__ == '__main__':
    app.run(debug=True, port=5000)