import whisper
import torch
import logging

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        # Select model based on available GPU memory
        if torch.cuda.is_available():
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)  # GB
            logger.info(f"Available GPU memory: {gpu_mem:.2f} GB")
            
            if gpu_mem > 6:
                model_name = "medium"
            else:
                model_name = "base"
                
            device = "cuda"
        else:
            model_name = "tiny"
            device = "cpu"
            
        logger.info(f"Loading Whisper model: {model_name} on {device}")
        self.model = whisper.load_model(model_name, device=device)
        self.model_type = model_name
    
    async def transcribe(self, audio_path):
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dict with transcript, detected language, and model used
        """
        logger.info(f"Starting transcription of {audio_path}")
        
        try:
            options = {
                "language": None,  # Auto-detect language
                "task": "transcribe",
                "fp16": torch.cuda.is_available()
            }
            
            # Special handling for small chunks
            try:
                result = self.model.transcribe(audio_path, **options)
            except RuntimeError as e:
                if "Failed to load audio" in str(e):
                    # Return empty result for corrupted audio chunks
                    logger.warning(f"Audio chunk too small or corrupted: {e}")
                    return {
                        "transcript": "",
                        "detected_language": "unknown",
                        "model_used": self.model_type
                    }
                else:
                    raise
                    
            detected_lang = result.get("language", "unknown")
            
            return {
                "transcript": result["text"].strip(),
                "detected_language": detected_lang,
                "model_used": self.model_type
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise