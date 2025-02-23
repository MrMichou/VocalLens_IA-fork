from pydantic import BaseModel
from typing import List, Optional, Dict

class TranscriptionResponse(BaseModel):
    transcript: str
    detected_language: str
    model_used: str

class QueryRequest(BaseModel):
    question: str

class QueryResult(BaseModel):
    text: str
    score: float
    metadata: Dict[str, str]

class QueryResponse(BaseModel):
    results: List[QueryResult]