from transformers import pipeline, AutoTokenizer
import torch
import logging
import gc
from typing import List, Dict
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def gpu_memory_guard():
    """Context manager to safely handle GPU operations with memory cleanup."""
    try:
        yield
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

class TranslationService:
    # Model configurations with fallbacks
    MODELS = {
        "fr-en": {
            "primary": "Helsinki-NLP/opus-mt-fr-en",
            "fallback": "facebook/nllb-200-distilled-600M"
        },
        "en-fr": {
            "primary": "Helsinki-NLP/opus-mt-en-fr",
            "fallback": "facebook/nllb-200-distilled-600M"
        }
    }
    
    # NLLB language codes for fallback model
    NLLB_CODES = {
        "en": "eng_Latn",
        "fr": "fra_Latn"
    }

    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.device = self._get_optimal_device()
        logger.info(f"Translation service initialized with device: {self.device}")
    
    def _get_optimal_device(self) -> str:
        """Determine the best device based on available hardware."""
        if not torch.cuda.is_available():
            return "cpu"
            
        # Check GPU memory
        try:
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)  # GB
            free_mem = gpu_mem - torch.cuda.memory_allocated(0) / (1024 ** 3)
            logger.info(f"GPU memory: {free_mem:.2f}GB free of {gpu_mem:.2f}GB")
            
            if free_mem < 1.5:  # Conservative threshold
                logger.warning(f"Limited GPU memory. Using CPU for translation.")
                return "cpu"
                
            return "cuda:0"
        except Exception as e:
            logger.warning(f"Error checking GPU: {e}. Using CPU.")
            return "cpu"
    
    def _get_model_key(self, source_lang: str, target_lang: str) -> str:
        """Create a key for the model dictionary."""
        return f"{source_lang}-{target_lang}"
    
    def _load_model(self, source_lang: str, target_lang: str, use_fallback: bool = False) -> bool:
        """Load translation model with proper error handling and fallbacks."""
        key = self._get_model_key(source_lang, target_lang)
        
        # Skip if already loaded
        if key in self.models and not use_fallback:
            return True
            
        with gpu_memory_guard():
            try:
                # Select model based on language pair and fallback setting
                model_type = "fallback" if use_fallback else "primary"
                if key not in self.MODELS:
                    logger.warning(f"Unsupported language pair: {key}. Using fallback.")
                    model_name = "facebook/nllb-200-distilled-600M"
                    is_multilingual = True
                else:
                    model_name = self.MODELS[key][model_type]
                    is_multilingual = "nllb" in model_name
                
                logger.info(f"Loading translation model: {model_name} for {key}")
                
                # For multilingual models (like NLLB)
                if is_multilingual:
                    src = self.NLLB_CODES.get(source_lang, source_lang)
                    tgt = self.NLLB_CODES.get(target_lang, target_lang)
                    
                    self.models[key] = pipeline(
                        "translation",
                        model=model_name,
                        device=0 if "cuda" in self.device else -1,
                        src_lang=src,
                        tgt_lang=tgt,
                    )
                else:
                    # For dedicated language-pair models (like Helsinki)
                    self.models[key] = pipeline(
                        "translation",
                        model=model_name,
                        device=0 if "cuda" in self.device else -1,
                    )
                
                # Load tokenizer for text chunking
                self.tokenizers[key] = AutoTokenizer.from_pretrained(model_name)
                logger.info(f"Successfully loaded model for {key}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load model for {key}: {e}")
                
                # If not already using fallback, try the fallback model
                if not use_fallback:
                    logger.info("Attempting fallback model...")
                    return self._load_model(source_lang, target_lang, use_fallback=True)
                    
                return False
    
    def _split_text(self, text: str, tokenizer) -> List[str]:
        """Split text into manageable chunks for translation."""
        max_length = 512  # Safe chunk size
        
        # First try paragraph splitting
        paragraphs = text.split('\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            tokens = tokenizer.encode(paragraph)
            token_count = len(tokens)
            
            # If paragraph fits in current chunk
            if current_length + token_count <= max_length:
                current_chunk.append(paragraph)
                current_length += token_count
            # If paragraph is too big on its own, split it
            elif token_count > max_length:
                # First, add current chunk if not empty
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Split big paragraph by sentences
                sentences = paragraph.replace('!', '.').replace('?', '.').split('.')
                sentences = [s.strip() + '.' for s in sentences if s.strip()]
                
                temp_chunk = []
                temp_length = 0
                
                for sentence in sentences:
                    sent_tokens = tokenizer.encode(sentence)
                    sent_length = len(sent_tokens)
                    
                    if temp_length + sent_length <= max_length:
                        temp_chunk.append(sentence)
                        temp_length += sent_length
                    else:
                        if temp_chunk:
                            chunks.append(' '.join(temp_chunk))
                            temp_chunk = [sentence]
                            temp_length = sent_length
                        # If a single sentence is too long, force split it
                        elif sent_length > max_length:
                            # Split by tokens and convert back to text
                            for i in range(0, sent_length, max_length):
                                token_chunk = sent_tokens[i:i + max_length]
                                chunks.append(tokenizer.decode(token_chunk, skip_special_tokens=True))
                        else:
                            temp_chunk = [sentence]
                            temp_length = sent_length
                            
                if temp_chunk:
                    chunks.append(' '.join(temp_chunk))
            else:
                # Start a new chunk with this paragraph
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_length = token_count
        
        # Add the last chunk if any
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        # Fallback for empty result
        if not chunks and text.strip():
            chunks = [text]
            
        return chunks

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text with robust error handling and recovery."""
        if not text or not text.strip():
            return ""
            
        # Same language = no translation needed
        if source_lang == target_lang:
            return text
            
        model_key = self._get_model_key(source_lang, target_lang)
        start_time = time.time()
        
        try:
            # Load model if needed
            if model_key not in self.models:
                success = self._load_model(source_lang, target_lang)
                if not success:
                    raise RuntimeError(f"Failed to load any translation model for {source_lang} to {target_lang}")
            
            # Check if we're using multilingual model
            is_multilingual = any(m in self.models[model_key].model.config._name_or_path for m in ["nllb", "mbart"])
            
            # Get language codes for multilingual models
            src_lang = self.NLLB_CODES.get(source_lang, source_lang) if is_multilingual else None
            tgt_lang = self.NLLB_CODES.get(target_lang, target_lang) if is_multilingual else None
            
            # Split into chunks
            chunks = self._split_text(text, self.tokenizers[model_key])
            
            # Process all chunks
            all_translations = []
            batch_size = 4  # Process in small batches to avoid memory issues
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                batch = [chunk for chunk in batch if chunk.strip()]  # Skip empty chunks
                
                if not batch:
                    continue
                    
                try:
                    # Different handling for multilingual models
                    if is_multilingual:
                        translations = self.models[model_key](
                            batch, 
                            src_lang=src_lang,
                            tgt_lang=tgt_lang,
                            max_length=768  # Allow longer outputs
                        )
                    else:
                        translations = self.models[model_key](
                            batch,
                            max_length=768
                        )
                        
                    # Extract translation text
                    batch_results = [item['translation_text'] for item in translations]
                    all_translations.extend(batch_results)
                    
                except RuntimeError as e:
                    if "CUDA out of memory" in str(e):
                        logger.warning("CUDA OOM during translation, trying smaller batch")
                        
                        # Process one by one
                        for chunk in batch:
                            try:
                                if is_multilingual:
                                    result = self.models[model_key](
                                        chunk, 
                                        src_lang=src_lang,
                                        tgt_lang=tgt_lang
                                    )
                                else:
                                    result = self.models[model_key](chunk)
                                    
                                all_translations.append(result[0]['translation_text'])
                            except RuntimeError:
                                # Last resort: fall back to CPU for this chunk
                                logger.warning("Falling back to CPU for problematic chunk")
                                
                                # Temporarily switch to CPU
                                prev_device = self.device
                                self.device = "cpu"
                                
                                # Reload model on CPU
                                with gpu_memory_guard():
                                    if model_key in self.models:
                                        del self.models[model_key]
                                    self._load_model(source_lang, target_lang)
                                
                                # Translate on CPU
                                if is_multilingual:
                                    result = self.models[model_key](
                                        chunk, 
                                        src_lang=src_lang,
                                        tgt_lang=tgt_lang
                                    )
                                else:
                                    result = self.models[model_key](chunk)
                                
                                all_translations.append(result[0]['translation_text'])
                                
                                # Restore device
                                self.device = prev_device
                    else:
                        raise
            
            # Join all translated chunks
            full_translation = ' '.join(all_translations)
            
            # Clean up whitespace and formatting
            full_translation = ' '.join(full_translation.split())
            full_translation = full_translation.replace(" .", ".").replace(" ,", ",")
            
            duration = time.time() - start_time
            logger.info(f"Translated {len(chunks)} chunks ({len(text)} chars) in {duration:.2f}s")
            
            return full_translation
            
        except Exception as e:
            logger.error(f"Translation error ({source_lang}->{target_lang}): {e}")
            
            # Try fallback if not already using it
            if model_key in self.models and "nllb" not in self.models[model_key].model.config._name_or_path:
                logger.info("Attempting translation with fallback model")
                
                # Clear current model
                with gpu_memory_guard():
                    if model_key in self.models:
                        del self.models[model_key]
                
                # Load and try fallback
                self._load_model(source_lang, target_lang, use_fallback=True)
                return await self.translate(text, source_lang, target_lang)
            
            # If we get here, all attempts failed
            raise RuntimeError(f"Translation failed after multiple attempts: {e}")
            
    async def cleanup(self):
        """Free memory by unloading models."""
        with gpu_memory_guard():
            self.models.clear()
            self.tokenizers.clear()
            logger.info("Translation service resources freed")