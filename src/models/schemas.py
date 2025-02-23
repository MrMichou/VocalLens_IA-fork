from pydantic import BaseModel
from typing import List, Optional

class TranscriptionResponse(BaseModel):
    transcript: str
    detected_language: str
    model_used: str
    translation: Optional[str] = None

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    results: List[str]

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str