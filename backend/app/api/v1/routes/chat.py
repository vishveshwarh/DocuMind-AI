from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.schemas import ChatRequest, ChatResponse, LangPreferenceRequest, LangPreferenceResponse
from app.services.rag_service import rag_service
from app.services.language_service import language_service
from app.logger import get_logger
from app.api.deps import verify_demo_key, get_client_ip
from app.services.rate_limit_service import rate_limit_service
from app.config import settings

logger = get_logger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    req: ChatRequest,
    _: bool = Depends(verify_demo_key),
):
    client_ip = get_client_ip(request)
    question = req.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if len(question) > settings.MAX_QUESTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Question too long. Max allowed is {settings.MAX_QUESTION_LENGTH} characters.",
        )

    rate_limit_service.check_chat_limit(client_ip)

    # Pre-check before Groq call
    rough_reserved_tokens = max(1, len(question.split())) + settings.CHAT_TOKEN_RESERVE
    rate_limit_service.ensure_token_budget_available(client_ip, rough_reserved_tokens)

    try:
        answer = rag_service.answer(question)
    except ValueError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate answer.")

    estimated_tokens = max(1, len(question.split()) + len(answer.split()))
    rate_limit_service.check_token_limit(client_ip, estimated_tokens)

    usage = rate_limit_service.get_usage(client_ip)

    return ChatResponse(
        answer=answer,
        language_used=language_service.lang_preference,
        usage=usage,
    )


@router.post("/set-language", response_model=LangPreferenceResponse)
def set_language(req: LangPreferenceRequest):
    if req.preference not in ["en", "original"]:
        raise HTTPException(status_code=400, detail="Preference must be 'en' or 'original'.")

    language_service.set_preference(req.preference)
    lang_name = language_service.get_language_name(language_service.detected_language)

    return LangPreferenceResponse(
        message=f"Language preference updated.",
        preference=req.preference
    )