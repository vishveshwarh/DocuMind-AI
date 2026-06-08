from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.routes import health, document, chat, usage

app = FastAPI(
    title=settings.APP_NAME,
    description="Upload a PDF and ask questions using RAG",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Demo-Key"],
)

# Versioned APIs
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(document.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(usage.router, prefix="/api/v1", tags=["Usage"])

# Old frontend compatibility
app.include_router(document.router, tags=["Documents Legacy"])
app.include_router(chat.router, tags=["Chat Legacy"])

@app.get("/")
def root():
    return {
        "status": "running",
        "docs": "/docs",
        "versioned_endpoints": {
            "health": "/api/v1/health/",
            "upload": "/api/v1/documents/upload",
            "chat": "/api/v1/chat",
            "set_language": "/api/v1/set-language",
        },
        "legacy_endpoints": {
            "upload": "/upload",
            "chat": "/chat",
        },
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )