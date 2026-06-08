# Handles embedding model and ChromaDB vector store.
# Uses one new Chroma folder per upload to avoid Windows file-lock issues.

import os
import uuid

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.current_vector_dir = None
        logger.info("Embedding model loaded successfully")

    def build_vectorstore(self, chunks: list) -> Chroma:
        """Build a new vectorstore for the latest uploaded PDF."""
        os.makedirs(settings.VECTOR_DIR, exist_ok=True)

        upload_id = uuid.uuid4().hex
        persist_directory = os.path.join(settings.VECTOR_DIR, upload_id)
        self.current_vector_dir = persist_directory

        logger.info(f"Building vectorstore with {len(chunks)} chunks at {persist_directory}")

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=settings.COLLECTION_NAME,
            persist_directory=persist_directory,
        )

        logger.info("Vectorstore built successfully")
        return vectorstore


embedding_service = EmbeddingService()
