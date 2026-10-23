"""HTTP endpoints for the DocuGraph API."""

import asyncio
import re
from functools import lru_cache

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from api.models import DocumentStatsResponse, ErrorResponse, IngestResponse, QueryRequest, QueryResponse
from config import settings
from services.ingest import IngestionError, PdfIngestionService
from services.indexing import IndexingService
from services.neo4j_handler import DocumentNotFoundError
from services.query import HybridQueryService

router = APIRouter()
_DOCUMENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@lru_cache(maxsize=1)
def get_indexing_service() -> IndexingService:
    return IndexingService()


def get_ingestion_service() -> PdfIngestionService:
    return PdfIngestionService(indexing_service=get_indexing_service())


@lru_cache(maxsize=1)
def get_query_service() -> HybridQueryService:
    return HybridQueryService()


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


@router.get(
    "/documents/{document_id}/stats",
    response_model=DocumentStatsResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def document_stats(
    document_id: str,
    indexing_service: IndexingService = Depends(get_indexing_service),
) -> DocumentStatsResponse:
    if not _DOCUMENT_ID.fullmatch(document_id):
        raise HTTPException(status_code=422, detail="Invalid document_id")
    try:
        result = await asyncio.to_thread(indexing_service.get_document_stats, document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Neo4j is unavailable") from exc
    return DocumentStatsResponse.model_validate(result)


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    query_service: HybridQueryService = Depends(get_query_service),
) -> QueryResponse:
    result = await query_service.search(
        request.query,
        document_id=request.document_id,
        top_k=request.top_k,
        graph_limit=request.graph_limit,
        max_hops=request.max_hops,
    )
    return QueryResponse.model_validate(result)
