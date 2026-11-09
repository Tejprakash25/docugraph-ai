"""Safe hybrid vector and graph query processing for Phase 4."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from config import settings
from services.embedding import EmbeddingService
from services.neo4j_handler import Neo4jStore
from services.qdrant_handler import QdrantStore
from services.rethinking import rethink_and_rank


_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_-]{1,63}")
_QUOTED = re.compile(r"[\"']([^\"']{2,80})[\"']")
_STOP_WORDS = {
    "what", "when", "where", "which", "who", "whom", "whose", "why", "how",
    "does", "did", "is", "are", "was", "were", "the", "a", "an", "and", "or",
    "of", "to", "in", "on", "for", "from", "with", "about", "show", "find",
    "tell", "me", "relationship", "relationships", "between", "document",
}


@dataclass(frozen=True)
class CypherPlan:
    query: str
    parameters: dict[str, Any]
    entity_names: list[str]
    confidence: float


@dataclass(frozen=True)
class VectorHit:
    chunk_id: str
    document_id: str
    page_number: int
    page_numbers: list[int]
    text: str
    confidence: float
    score: float


@dataclass(frozen=True)
class GraphHit:
    source: str
    source_type: str
    predicate: str
    target: str
    target_type: str
    confidence: float
    evidence: str | None
    chunk_ids: list[str]
    pages: list[Any]
    score: float
    path: list[dict[str, Any]] = field(default_factory=list)
    hops: int = 0


class SafeCypherTranslator:
    """Translate natural language into one fixed, parameterized graph query."""

    def translate(
        self,
        query_text: str,
        *,
        document_id: str | None,
        limit: int,
        max_hops: int,
    ) -> CypherPlan:
        quoted = [re.sub(r"\s+", " ", value).strip() for value in _QUOTED.findall(query_text)]
        words = [word for word in _WORD.findall(query_text) if word.casefold() not in _STOP_WORDS]
        candidates: list[str] = []
        for value in quoted + words:
            if value.casefold() not in {item.casefold() for item in candidates}:
                candidates.append(value)
        candidates = candidates[:12]
        return CypherPlan(
            query="fixed_parameterized_relationship_search",
            parameters={
                "entity_names": candidates,
                "document_id": document_id,
                "limit": max(1, min(limit, 50)),
                "max_hops": max(1, min(max_hops, 3)),
            },
            entity_names=candidates,
            confidence=0.9 if quoted else 0.75,
        )


class HybridQueryService:
    def __init__(
        self,
        qdrant: Any | None = None,
        neo4j: Any | None = None,
        embedder: EmbeddingService | None = None,
        translator: SafeCypherTranslator | None = None,
    ) -> None:
        self.qdrant = qdrant or QdrantStore()
        self.neo4j = neo4j or Neo4jStore()
        self.embedder = embedder or EmbeddingService()
        self.translator = translator or SafeCypherTranslator()

    async def search(
        self,
        query_text: str,
        *,
        document_id: str | None = None,
        top_k: int = 8,
        graph_limit: int = 20,
        max_hops: int = 2,
    ) -> dict[str, Any]:
        vector = (await self.embedder.embed_texts([query_text]))[0]
        vector_rows = await self._search_vectors(vector, top_k, document_id)
        plan = self.translator.translate(
            query_text, document_id=document_id, limit=graph_limit, max_hops=max_hops
        )
        graph_rows = await self._search_graph(plan)
        vector_hits = [VectorHit(**row) for row in vector_rows]
        graph_hits = [GraphHit(**row) for row in graph_rows]
        fused = await rethink_and_rank(
            vector,
            vector_hits,
            graph_hits,
            settings,
            top_k=top_k,
            embedder=self.embedder,
        )
        missing_text_ids = list(dict.fromkeys(
            row["chunk_id"] for row in fused if not row.get("text")
        ))
        if missing_text_ids:
            import asyncio

            chunk_rows = await asyncio.to_thread(self.neo4j.get_chunks, missing_text_ids)
            chunks_by_id = {row["chunk_id"]: row for row in chunk_rows}
            hydrated = []
            for row in fused:
                if row.get("text"):
                    hydrated.append(row)
                    continue
                chunk = chunks_by_id.get(row["chunk_id"])
                if (
                    chunk is None
                    or not str(chunk.get("text") or "").strip()
                    or not chunk.get("page_number")
                ):
                    continue
                hydrated.append(
                    {
                        **row,
                        "document_id": chunk["document_id"],
                        "page_number": chunk["page_number"],
                        "page_numbers": chunk.get("page_numbers") or [],
                        "text": chunk["text"],
                    }
                )
            fused = hydrated
        return {
            "query": query_text,
            "vector_results": [hit.__dict__ for hit in vector_hits],
            "graph_results": [hit.__dict__ for hit in graph_hits],
            "fused_results": fused,
            "query_plan": {
                "translator": "safe_parameterized_template",
                "entity_terms": plan.entity_names,
                "confidence": plan.confidence,
            },
        }

    async def _search_vectors(self, vector: list[float], top_k: int, document_id: str | None) -> list[dict[str, Any]]:
        import asyncio

        try:
            return await asyncio.to_thread(
                self.qdrant.search_chunks, vector=vector, limit=top_k, document_id=document_id
            )
        except Exception:
            return []

    async def _search_graph(self, plan: CypherPlan) -> list[dict[str, Any]]:
        import asyncio

        if not plan.entity_names:
            return []
        try:
            return await asyncio.to_thread(
                self.neo4j.search_graph,
                entity_names=plan.entity_names,
                limit=plan.parameters["limit"],
                document_id=plan.parameters["document_id"],
                max_hops=plan.parameters["max_hops"],
            )
        except Exception:
            return []
