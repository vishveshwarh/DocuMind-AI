import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.schemas import UploadResponse
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service
from app.services.language_service import language_service
from app.config import settings
from app.logger import get_logger
from app.api.deps import verify_demo_key, get_client_ip
from app.services.rate_limit_service import rate_limit_service

logger = get_logger(__name__)
router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    _: bool = Depends(verify_demo_key),
):
    client_ip = get_client_ip(request)
    tmp_path = None

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        logger.warning(f"Invalid file type uploaded: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(file_bytes) > settings.MAX_PDF_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"PDF too large. Max allowed size is {settings.MAX_PDF_MB} MB.",
        )

    # Count only valid upload attempts against the daily demo budget.
    rate_limit_service.check_upload_limit(client_ip)

    logger.info(f"Upload started: {file.filename}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} pages from {file.filename}")

        if not documents:
            raise HTTPException(status_code=400, detail="No readable pages found in this PDF.")

        if len(documents) > settings.MAX_PDF_PAGES:
            raise HTTPException(
                status_code=400,
                detail=f"PDF has too many pages. Max allowed is {settings.MAX_PDF_PAGES} pages.",
            )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")

        if not chunks:
            raise HTTPException(status_code=400, detail="No readable text found in this PDF.")

        sample_text = chunks[0].page_content if chunks else ""
        detected_lang = language_service.detect_language(sample_text)
        lang_name = language_service.get_language_name(detected_lang)

        vectorstore = embedding_service.build_vectorstore(chunks)
        retriever = vectorstore.as_retriever(search_kwargs={"k": settings.RETRIEVER_K})

        rag_service.build_chain(
            retriever=retriever,
            language_instruction_fn=language_service.get_prompt_instruction,
        )

        logger.info(
            f"Upload complete: {file.filename} | {len(chunks)} chunks | lang: {detected_lang}"
        )

        return UploadResponse(
            message=f"PDF loaded successfully. {len(chunks)} chunks indexed. Ready to chat!",
            chunks=len(chunks),
            detected_language=detected_lang,
            language_name=lang_name,
            is_english=language_service.is_english(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Upload failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process PDF. Please try another file.",
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            logger.info("Temp file cleaned up")
