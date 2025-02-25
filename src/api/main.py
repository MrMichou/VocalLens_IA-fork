from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from fastapi.middleware.cors import CORSMiddleware
import os
from ..models.schemas import TranscriptionResponse, QueryRequest, QueryResponse, TranslationRequest
from ..services.whisper_service import WhisperService
from ..services.qdrant_service import QdrantService
from ..services.translation_service import TranslationService

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
translation_service = TranslationService()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting VocalLens API")
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Cleaning up resources")
    await qdrant_service.cleanup()
    if hasattr(translation_service, 'cleanup'):
        await translation_service.cleanup()

def store_transcript_in_qdrant(transcript: str, metadata: dict):
    """Background task to store transcript data."""
    try:
        import asyncio
        asyncio.run(qdrant_service.add_transcript(transcript, metadata))
    except Exception as e:
        logger.error(f"Background storage failed: {e}")

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(audio: UploadFile = File(...), background_tasks: BackgroundTasks = None):
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
        
        # Prepare metadata
        metadata = {
            "timestamp": audio.filename,  # À améliorer
            "detected_language": result["detected_language"],
            "model_used": result["model_used"]
        }
        
        # Store in Qdrant in background to avoid blocking
        if background_tasks:
            background_tasks.add_task(store_transcript_in_qdrant, result["transcript"], metadata)
        else:
            # Try to store but don't fail if storage fails
            try:
                storage_success = await qdrant_service.add_transcript(result["transcript"], metadata)
                if not storage_success:
                    logger.warning("Transcript was not stored in vector database")
            except Exception as e:
                logger.error(f"Failed to store transcript: {e}")
        
        # Add translation if needed
        if result["detected_language"] == "fr":
            try:
                result["translation"] = await translation_service.translate(
                    result["transcript"],
                    "fr",
                    "en"
                )
            except Exception as e:
                logger.error(f"Translation failed: {e}")
                result["translation"] = None
        
        return result
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="No question provided")
    
    try:
        results = await qdrant_service.search(request.question)
        return QueryResponse(results=results)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate(request: TranslationRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        translation = await translation_service.translate(
            request.text,
            request.source_lang,
            request.target_lang
        )
        return {
            "translation": translation
        }
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}