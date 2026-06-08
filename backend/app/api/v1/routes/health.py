from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import settings

router = APIRouter()

@router.get("/", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="running",
        version=settings.APP_VERSION,
        vector_db="ChromaDB (local)"
    )