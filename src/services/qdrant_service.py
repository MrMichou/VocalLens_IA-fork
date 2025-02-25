from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, OptimizersConfigDiff
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
import logging
from ..config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(settings.qdrant_host, port=settings.qdrant_port)
        self.collection_name = settings.collection_name
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embeddings_model,
            model_kwargs={'device': settings.device}
        )
        self._init_collection()
        self.vector_store = self._init_vector_store()

    def _init_collection(self):
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating new collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                    optimizers_config=OptimizersConfigDiff(
                        default_segment_number=2,
                        indexing_threshold=20000,  # Higher threshold to batch more
                        vacuum_min_vector_number=1000,  # Clean up space when possible
                        max_optimization_threads=2
                    )
                )
            else:
                # Try to optimize existing collection
                try:
                    logger.info(f"Collection {self.collection_name} exists, checking if optimization needed")
                    self.client.update_collection(
                        collection_name=self.collection_name,
                        optimizers_config=OptimizersConfigDiff(
                            vacuum_min_vector_number=1000,  # Trigger cleanup
                        )
                    )
                except Exception as e:
                    logger.warning(f"Could not optimize collection: {e}")
                    
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")
            raise

    def _init_vector_store(self):
        try:
            return Qdrant(
                client=self.client,
                collection_name=self.collection_name,
                embeddings=self.embeddings
            )
        except Exception as e:
            logger.error(f"Error initializing Qdrant vector store: {e}")
            raise

    async def add_transcript(self, text: str, metadata: dict):
        try:
            self.vector_store.add_texts(
                texts=[text],
                metadatas=[metadata]
            )
            logger.info(f"Added transcript to Qdrant ({len(text)} chars)")
            return True
        except Exception as e:
            logger.error(f"Failed to add transcript to Qdrant: {e}")
            # Don't raise exception - allow transcription to continue without storage
            return False

    async def search(self, query: str, k: int = 3):
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return [
                {
                    "text": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                }
                for doc, score in results
            ]
        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}")
            return []  # Return empty results on error
            
    async def cleanup(self):
        """Remove old entries to free up space."""
        try:
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            vectors_count = collection_info.vectors_count
            
            if vectors_count > 1000:
                # If we have many vectors, trigger optimization explicitly
                logger.info(f"Cleaning up Qdrant collection with {vectors_count} vectors")
                self.client.update_collection(
                    collection_name=self.collection_name,
                    optimizers_config=OptimizersConfigDiff(
                        vacuum_min_vector_number=500,  # Lower threshold to trigger cleanup
                    )
                )
                
            return True
        except Exception as e:
            logger.error(f"Error cleaning up Qdrant: {e}")
            return False