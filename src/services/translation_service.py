from transformers import pipeline
import torch
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.translator = pipeline(
            "translation",
            model="Helsinki-NLP/opus-mt-fr-en",
            device=0 if torch.cuda.is_available() else -1
        )
        self.reverse_translator = pipeline(
            "translation",
            model="Helsinki-NLP/opus-mt-en-fr",
            device=0 if torch.cuda.is_available() else -1
        )
        
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            if source_lang == "fr" and target_lang == "en":
                result = self.translator(text, max_length=512)
            elif source_lang == "en" and target_lang == "fr":
                result = self.reverse_translator(text, max_length=512)
            else:
                raise ValueError(f"Unsupported language pair: {source_lang}-{target_lang}")
            
            return result[0]['translation_text']
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise