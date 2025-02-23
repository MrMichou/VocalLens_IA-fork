from pydantic_settings import BaseSettings
import torch

class Settings(BaseSettings):
    # Device Configuration
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    gpu_memory_threshold: int = 4 * (1024**3)

    # Whisper Configuration 
    whisper_model_size: str = "base"

    # Qdrant Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "meeting_transcripts"

    # Model Configuration
    embeddings_model: str = "dangvantuan/sentence-camembert-base"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "ignore"