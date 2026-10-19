"""In-memory PDF ingestion pipeline for Phase 2."""

from __future__ import annotations

import asyncio
import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Any

import fitz

from config import settings
from services.extraction import Entity, ExtractionResult, Relationship, ResilientExtractor


class IngestionError(ValueError):
    """Raised when an uploaded document cannot be safely ingested."""


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str
    start_offset: int
    end_offset: int


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    text: str
    page_number: int
    page_numbers: list[int]
    token_count: int
    start_offset: int
    end_offset: int


@dataclass
class ParsedDocument:
    document_id: str
    filename: str
    content_hash: str
    page_count: int
    pages: list[PageText]
    chunks: list[DocumentChunk]


@dataclass
class IngestionSummary:
    document_id: str
    chunks_created: int
    entities_extracted: int
    relationships_extracted: int
    avg_confidence: float
    pages: int
    processing_time_seconds: float
    chunks: list[DocumentChunk] = field(default_factory=list)
    extractions: dict[str, ExtractionResult] = field(default_factory=dict)
    indexing: dict[str, str] = field(default_factory=dict)


TOKEN_PATTERN = re.compile(r"\S+")


def _validate_pdf(content: bytes, filename: str, max_upload_size_mb: int) -> None:
    if not content:
        raise IngestionError("Uploaded file is empty")
    if len(content) > max_upload_size_mb * 1024 * 1024:
        raise IngestionError(f"PDF exceeds the {max_upload_size_mb} MB upload limit")
    if not content.startswith(b"%PDF"):
        raise IngestionError("Uploaded file is not a valid PDF")
    if filename and not filename.lower().endswith(".pdf"):
        raise IngestionError("Only PDF files are accepted")


def _page_texts(document: fitz.Document) -> tuple[list[PageText], str]:
    pages: list[PageText] = []
    document_text_parts: list[str] = []
    offset = 0
    for index, page in enumerate(document, start=1):
        text = page.get_text("text").replace("\x00", "").strip()
        if not text:
            continue
        if document_text_parts:
            document_text_parts.append("\n")
            offset += 1
        start = offset
        document_text_parts.append(text)
        offset += len(text)
        pages.append(PageText(index, text, start, offset))
    return pages, "".join(document_text_parts)


def _page_for_offset(pages: list[PageText], offset: int) -> int:
    for page in pages:
        if page.start_offset <= offset < page.end_offset:
            return page.page_number
    return pages[-1].page_number


def parse_pdf(
    content: bytes,
    document_id: str,
    filename: str = "document.pdf",
    *,
    chunk_size_tokens: int | None = None,
    chunk_overlap_tokens: int | None = None,
    max_upload_size_mb: int | None = None,
) -> ParsedDocument:
    """Parse a PDF without writing the original upload to disk."""
    max_size = max_upload_size_mb or settings.max_upload_size_mb
    _validate_pdf(content, filename, max_size)
    chunk_size = chunk_size_tokens or settings.chunk_size_tokens
    overlap = chunk_overlap_tokens if chunk_overlap_tokens is not None else settings.chunk_overlap_tokens
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise IngestionError("Chunk size and overlap settings are invalid")

    try:
        document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise IngestionError("PDF parsing failed") from exc

    try:
        pages, full_text = _page_texts(document)
        page_count = len(document)
    finally:
        document.close()

    if not pages or not full_text.strip():
        raise IngestionError("PDF contains no extractable text")

    tokens = list(TOKEN_PATTERN.finditer(full_text))
    chunks: list[DocumentChunk] = []
    step = chunk_size - overlap
    for start in range(0, len(tokens), step):
        window = tokens[start : start + chunk_size]
        if not window:
            break
        start_offset = window[0].start()
        end_offset = window[-1].end()
        page_numbers = list(dict.fromkeys(_page_for_offset(pages, token.start()) for token in window))
        chunks.append(
            DocumentChunk(
                chunk_id=f"{document_id}_chunk_{len(chunks) + 1}",
                document_id=document_id,
                text=full_text[start_offset:end_offset],
                page_number=page_numbers[0],
                page_numbers=page_numbers,
                token_count=len(window),
                start_offset=start_offset,
                end_offset=end_offset,
            )
        )
        if start + chunk_size >= len(tokens):
            break
    return ParsedDocument(document_id, filename, hashlib.sha256(content).hexdigest(), page_count, pages, chunks)


class PdfIngestionService:
    def __init__(self, extractor: Any | None = None, indexing_service: Any | None = None) -> None:
        self.indexing_service = indexing_service
        self.extractor = extractor or ResilientExtractor(
            groq_api_key=settings.groq_api_key,
            gemini_api_key=settings.gemini_api_key,
            groq_model=settings.groq_model,
            gemini_model=settings.gemini_model,
            timeout=settings.llm_timeout_seconds,
        )

    async def ingest(
        self,
        content: bytes,
        document_id: str,
        filename: str,
        document_type: str | None = None,
    ) -> IngestionSummary:
        return await self._ingest_async(content, document_id, filename, document_type)

    def ingest_bytes(
        self,
        content: bytes,
        document_id: str,
        filename: str,
        document_type: str | None = None,
    ) -> IngestionSummary:
        """Synchronous convenience API used by local scripts and unit tests."""
        return asyncio.run(self._ingest_async(content, document_id, filename, document_type))

    async def _ingest_async(
        self,
        content: bytes,
        document_id: str,
        filename: str,
        document_type: str | None = None,
    ) -> IngestionSummary:
        started = time.perf_counter()
        parsed = parse_pdf(content, document_id, filename)
        semaphore = asyncio.Semaphore(max(1, settings.extraction_concurrency))

        async def extract_chunk(chunk: DocumentChunk) -> tuple[str, ExtractionResult]:
            async with semaphore:
                return chunk.chunk_id, await self.extractor.extract(chunk.text)

        extracted = dict(await asyncio.gather(*(extract_chunk(chunk) for chunk in parsed.chunks)))
        entities: list[Entity] = []
        relationships: list[Relationship] = []
        confidences: list[float] = []
        for result in extracted.values():
            entities.extend(result.entities)
            relationships.extend(result.relationships)
            confidences.extend(result.confidence_values)
        average = sum(confidences) / len(confidences) if confidences else 0.0
        indexing = {}
        if self.indexing_service is not None:
            index_result = await self.indexing_service.index_document(
                document_id, parsed, extracted, document_type
            )
            indexing = {"neo4j": index_result.neo4j, "qdrant": index_result.qdrant}
        return IngestionSummary(
            document_id=document_id,
            chunks_created=len(parsed.chunks),
            entities_extracted=len(entities),
            relationships_extracted=len(relationships),
            avg_confidence=round(average, 4),
            pages=parsed.page_count,
            processing_time_seconds=round(time.perf_counter() - started, 4),
            chunks=parsed.chunks,
            extractions=extracted,
            indexing=indexing,
        )
