"""HTTP endpoints for the DocuGraph API."""

import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from api.models import ErrorResponse, IngestResponse
from config import settings
from services.ingest import IngestionError, PdfIngestionService

router = APIRouter()
_DOCUMENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def get_ingestion_service() -> PdfIngestionService:
    return PdfIngestionService()


@router.post(
    "/ingest",
    response_model=IngestResponse,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
    status_code=status.HTTP_200_OK,
)
async def ingest_document(
    document_id: str = Form(..., min_length=1, max_length=128),
    file: UploadFile = File(...),
    document_type: str | None = Form(default=None, max_length=64),
    ingestion_service: PdfIngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    if not _DOCUMENT_ID.fullmatch(document_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="document_id must contain only letters, numbers, underscores, and hyphens",
        )
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"PDF exceeds the {settings.max_upload_size_mb} MB upload limit",
        )
    try:
        summary = await ingestion_service.ingest(
            content,
            document_id=document_id,
            filename=file.filename,
            document_type=document_type,
        )
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Document ingestion failed") from exc
    finally:
        await file.close()

    return IngestResponse(
        document_id=summary.document_id,
        chunks_created=summary.chunks_created,
        entities_extracted=summary.entities_extracted,
        relationships_extracted=summary.relationships_extracted,
        avg_confidence=summary.avg_confidence,
        pages=summary.pages,
        processing_time_seconds=summary.processing_time_seconds,
    )
