import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # ── API ────────────────────────────────────────────────────────────
    APP_NAME: str = os.getenv("APP_NAME", "DocuMind AI")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8001"))

    # ── Groq LLM ───────────────────────────────────────────────────────
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0"))

    # ── ChromaDB ───────────────────────────────────────────────────────
    VECTOR_DIR: str = os.getenv("VECTOR_DIR", "./chroma_db")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "rag_documents")
    RETRIEVER_K: int = int(os.getenv("RETRIEVER_K", "3"))

    # ── Embeddings ─────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    # ── Chunking ───────────────────────────────────────────────────────
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # ── CORS & Environment ─────────────────────────────────────────────
    # ENV controls behaviour — set to "production" on Render
    ENV: str = os.getenv("ENV", "development")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # ── Logging ────────────────────────────────────────────────────────
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ── Language display names ─────────────────────────────────────────
    LANGUAGE_NAMES: dict = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "zh-cn": "Chinese",
        "ar": "Arabic",
        "ja": "Japanese",
    }

    # ── Demo protection ────────────────────────────────────────────────
    # Set DEMO_ACCESS_KEY on Render — frontend must send it as X-Demo-Key header
    DEMO_ACCESS_KEY: str = os.getenv("DEMO_ACCESS_KEY", "")

    # ── File & request limits ──────────────────────────────────────────
    MAX_PDF_MB: int = int(os.getenv("MAX_PDF_MB", "5"))
    MAX_PDF_BYTES: int = MAX_PDF_MB * 1024 * 1024
    MAX_PDF_PAGES: int = int(os.getenv("MAX_PDF_PAGES", "20"))
    MAX_QUESTION_LENGTH: int = int(os.getenv("MAX_QUESTION_LENGTH", "500"))

    # ── Rate limits (in-memory v1 — move to Redis later) ───────────────
    DAILY_REQUEST_LIMIT: int = int(os.getenv("DAILY_REQUEST_LIMIT", "50"))
    DAILY_UPLOAD_LIMIT: int = int(os.getenv("DAILY_UPLOAD_LIMIT", "5"))
    DAILY_TOKEN_LIMIT: int = int(os.getenv("DAILY_TOKEN_LIMIT", "50000"))
    CHAT_TOKEN_RESERVE: int = int(os.getenv("CHAT_TOKEN_RESERVE", "1500"))

    # ── CORS origins — computed as property so ENV is read at call time ─
    # FIX: class-level if/else runs at import time before .env is loaded,
    # so ENV was always "development". Property fixes this.
    @property
    def ALLOWED_ORIGINS(self) -> list:
        if self.ENV == "production":
            # Production: only allow the deployed frontend URL
            return [self.FRONTEND_ORIGIN]
        # Development: allow localhost variants
        return [
            self.FRONTEND_ORIGIN,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]


settings = Settings()
