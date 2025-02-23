from fastapi import FastAPI, UploadFile, File, HTTPException
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from fastapi.middleware.cors import CORSMiddleware
import os
from ..models.schemas import TranscriptionResponse, QueryRequest, QueryResponse
from ..services.whisper_service import WhisperService
from ..services.qdrant_service import QdrantService

app = FastAPI(title="VocalLens-AI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajuster pour la production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
whisper_service = WhisperService()
qdrant_service = QdrantService()

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(audio: UploadFile = File(...)):
    if not audio:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    temp_path = f"temp_{audio.filename}"
    try:
        # Sauvegarder le fichier temporairement
        content = await audio.read()
        with open(temp_path, "wb") as temp_file:
            temp_file.write(content)
        
        # Transcrire
        result = await whisper_service.transcribe(temp_path)
        
        # Stocker dans Qdrant
        metadata = {
            "timestamp": audio.filename,  # À améliorer
            "detected_language": result["detected_language"],
            "model_used": result["model_used"]
        }
        await qdrant_service.add_transcript(result["transcript"], metadata)
        
        return result
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="No question provided")
    
    results = await qdrant_service.search(request.question)
    return {"results": results}