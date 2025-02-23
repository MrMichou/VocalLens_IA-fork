import whisper
import torch
import gc
import logging
from ..config import Settings

logger = logging.getLogger(__name__)

settings = Settings()

class WhisperService:
    def __init__(self):
        self.model = None
        self.device = settings.device
        self.model_size = self._determine_model_size()
        self._load_model()

    def _determine_model_size(self) -> str:
        logger.info(f"Determining model size for device: {self.device}")
        if self.device == "cuda":
            available_memory = self._get_available_gpu_memory()
            return "medium" if available_memory >= settings.gpu_memory_threshold else "base"
        return "base"

    def _get_available_gpu_memory(self) -> int:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
            return torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)
        return 0

    def _load_model(self):
        logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
        if self.device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()
        self.model = whisper.load_model(self.model_size, device=self.device)

    async def transcribe(self, audio_path: str) -> dict:
        logger.info(f"Starting transcription of {audio_path}")
        try:
            if self.device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()

            result = self.model.transcribe(
                audio_path,
                language="fr",
                task="transcribe",
                initial_prompt="Ceci est une transcription en français."
            )

            logger.info(f"Transcription completed. Detected language: {result.get('language', 'unknown')}")
            return {
                "transcript": result["text"],
                "detected_language": result.get("language", "unknown"),
                "model_used": self.model_size
            }
        finally:
            if self.device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()