from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, OptimizersConfigDiff
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from ..config import Settings

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
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                optimizers_config=OptimizersConfigDiff(
                    default_segment_number=2,
                    max_optimization_threads=2
                )
            )

    def _init_vector_store(self):
        return Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )

    async def add_transcript(self, text: str, metadata: dict):
        self.vector_store.add_texts(
            texts=[text],
            metadatas=[metadata]
        )

    async def search(self, query: str, k: int = 3):
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return [
            {
                "text": doc.page_content,
                "score": float(score),
                "metadata": doc.metadata
            }
            for doc, score in results
        ]