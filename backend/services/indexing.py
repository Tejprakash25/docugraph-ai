"""Coordinates Neo4j and Qdrant indexing for an ingested document."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from services.embedding import EmbeddingService
from services.extraction import ExtractionResult
from services.ingest import DocumentChunk, ParsedDocument
from services.neo4j_handler import Neo4jStore
from services.qdrant_handler import QdrantStore


@dataclass
class IndexingResult:
    neo4j: str = "not_attempted"
    qdrant: str = "not_attempted"
    errors: list[str] = field(default_factory=list)


class IndexingService:
    def __init__(
        self,
        neo4j: Any | None = None,
        qdrant: Any | None = None,
        embedder: EmbeddingService | None = None,
    ) -> None:
        self.neo4j = neo4j or Neo4jStore()
        self.qdrant = qdrant or QdrantStore()
        self.embedder = embedder or EmbeddingService()

    async def index_document(
        self,
        document_id: str,
        parsed: ParsedDocument,
        extractions: dict[str, ExtractionResult],
        document_type: str | None,
    ) -> IndexingResult:
        result = IndexingResult()
        chunks = [
            {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "page_number": chunk.page_number,
                "page_numbers": chunk.page_numbers,
                "text": chunk.text,
                "start_offset": chunk.start_offset,
                "end_offset": chunk.end_offset,
                "token_count": chunk.token_count,
            }
            for chunk in parsed.chunks
        ]
        entities: list[dict[str, Any]] = []
        relationships: list[dict[str, Any]] = []
        for chunk in parsed.chunks:
            extraction = extractions.get(chunk.chunk_id, ExtractionResult())
            for entity in extraction.entities:
                entities.append(
                    {
                        "name": entity.name,
                        "type": entity.type,
                        "confidence": entity.confidence,
                        "chunk_id": chunk.chunk_id,
                    }
                )
            for relationship in extraction.relationships:
                relationships.append(
                    {
                        "document_id": document_id,
                        "source": relationship.source,
                        "predicate": relationship.predicate,
                        "target": relationship.target,
                        "confidence": relationship.confidence,
                        "evidence": relationship.evidence,
                        "source_chunk_ids": [chunk.chunk_id],
                        "source_pages": chunk.page_numbers,
                    }
                )

        try:
            await asyncio.to_thread(
                self.neo4j.upsert_document,
                document_id=document_id,
                filename=parsed.filename,
                content_hash=parsed.content_hash,
                num_pages=parsed.page_count,
                document_type=document_type,
                chunks=chunks,
            )
            await asyncio.to_thread(
                self.neo4j.upsert_extractions,
                document_id=document_id,
                entities=entities,
                relationships=relationships,
            )
            result.neo4j = "indexed"
        except Exception as exc:
            result.neo4j = "unavailable"
            result.errors.append(f"neo4j: {exc}")

        try:
            qdrant_available = await asyncio.to_thread(self.qdrant.health)
            if not qdrant_available:
                result.qdrant = "unavailable"
                result.errors.append("qdrant: health check failed")
                return result
            vectors = await self.embedder.embed_texts([chunk.text for chunk in parsed.chunks])
            points = []
            for chunk, vector in zip(parsed.chunks, vectors, strict=True):
                extraction = extractions.get(chunk.chunk_id, ExtractionResult())
                confidence_values = extraction.confidence_values
                points.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "vector": vector,
                        "payload": {
                            "chunk_id": chunk.chunk_id,
                            "document_id": chunk.document_id,
                            "page_number": chunk.page_number,
                            "page_numbers": chunk.page_numbers,
                            "text": chunk.text,
                            "start_offset": chunk.start_offset,
                            "end_offset": chunk.end_offset,
                            "confidence": max(confidence_values) if confidence_values else 0.0,
                        },
                    }
                )
            await asyncio.to_thread(self.qdrant.upsert_chunks, points=points)
            result.qdrant = "indexed"
        except Exception as exc:
            result.qdrant = "unavailable"
            result.errors.append(f"qdrant: {exc}")
        return result

    def get_document_stats(self, document_id: str) -> dict[str, Any]:
        return self.neo4j.get_document_stats(document_id)

    def health(self) -> dict[str, str]:
        return {
            "neo4j": "connected" if self.neo4j.health() else "disconnected",
            "qdrant": "connected" if self.qdrant.health() else "disconnected",
        }
