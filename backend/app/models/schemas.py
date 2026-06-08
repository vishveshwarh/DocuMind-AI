# All Pydantic models — request bodies and response shapes
# Keeps API contracts clear and documented

from pydantic import BaseModel
from typing import Optional

# ── Request models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str

class LangPreferenceRequest(BaseModel):
    preference: str   # "en" or "original"

# ── Response models ─────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    vector_db: str

class UploadResponse(BaseModel):
    message: str
    chunks: int
    detected_language: str
    language_name: str
    is_english: bool

class ChatResponse(BaseModel):
    answer: str
    language_used: Optional[str] = None

class LangPreferenceResponse(BaseModel):
    message: str
    preference: str