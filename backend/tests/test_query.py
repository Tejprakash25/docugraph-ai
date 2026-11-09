import asyncio

import pytest
from pydantic import ValidationError

from api.models import QueryRequest
from services.embedding import EmbeddingService
from services.query import HybridQueryService, SafeCypherTranslator


class FakeQdrant:
    def search_chunks(self, **kwargs):
        assert len(kwargs["vector"]) == 384
        return [
            {
                "chunk_id": "contract_001_chunk_1",
                "document_id": "contract_001",
                "page_number": 1,
                "page_numbers": [1],
                "text": "Alice signs Acme Corp.",
                "confidence": 0.9,
                "score": 0.95,
            }
        ]


class FakeNeo4j:
    def search_graph(self, **kwargs):
        assert kwargs["entity_names"]
        return [
            {
                "source": "Alice",
                "source_type": "Person",
                "predicate": "signs",
                "target": "Acme Corp",
                "target_type": "Organization",
                "confidence": 0.8,
                "evidence": "Alice signs Acme Corp.",
                "chunk_ids": ["contract_001_chunk_1"],
                "pages": [[1]],
                "score": 0.8,
            }
        ]


class EmptyQdrant:
    def search_chunks(self, **kwargs):
        return []


class GraphOnlyNeo4j:
    def __init__(self, chunks):
        self.chunks = chunks
        self.requested_chunk_ids = None

    def search_graph(self, **kwargs):
        return [
            {
                "source": "Jordan",
                "source_type": "Person",
                "predicate": "works_for",
                "target": "Acme",
                "target_type": "Organization",
                "confidence": 0.8,
                "evidence": "Jordan works for Acme",
                "chunk_ids": ["chunk-1"],
                "pages": [],
                "score": 0.8,
            }
        ]

    def get_chunks(self, chunk_ids):
        self.requested_chunk_ids = chunk_ids
        return self.chunks


def test_translator_returns_fixed_parameterized_plan() -> None:
    plan = SafeCypherTranslator().translate(
        'What is the relationship between "Alice" and Acme?',
        document_id="contract_001",
        limit=20,
        max_hops=2,
    )

    assert plan.query == "fixed_parameterized_relationship_search"
    assert "Alice" in plan.entity_names
    assert plan.parameters["document_id"] == "contract_001"
    assert "MATCH" not in plan.parameters["entity_names"]


def test_query_max_hops_allows_three_and_translator_caps_at_three() -> None:
    assert QueryRequest(query="find relationships").max_hops == 2
    assert QueryRequest(query="find relationships", max_hops=3).max_hops == 3
    with pytest.raises(ValidationError):
        QueryRequest(query="find relationships", max_hops=4)

    plan = SafeCypherTranslator().translate(
        "find relationships",
        document_id=None,
        limit=20,
        max_hops=99,
    )
    assert plan.parameters["max_hops"] == 3


def test_hybrid_search_fuses_vector_and_graph_scores() -> None:
    service = HybridQueryService(
        qdrant=FakeQdrant(),
        neo4j=FakeNeo4j(),
        embedder=EmbeddingService(force_fallback=True),
    )

    result = asyncio.run(service.search("Who does Alice sign with?"))

    assert len(result["vector_results"]) == 1
    assert len(result["graph_results"]) == 1
    assert result["fused_results"][0]["chunk_id"] == "contract_001_chunk_1"
    assert result["fused_results"][0]["score"] > 0


def test_graph_only_hit_is_hydrated_with_chunk_text_and_page() -> None:
    neo4j = GraphOnlyNeo4j(
        [
            {
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "page_number": 4,
                "page_numbers": [4, 5],
                "text": "Jordan works for Acme.",
            }
        ]
    )
    service = HybridQueryService(
        qdrant=EmptyQdrant(),
        neo4j=neo4j,
        embedder=EmbeddingService(force_fallback=True),
    )

    result = asyncio.run(service.search("Who is Jordan?"))

    assert neo4j.requested_chunk_ids == ["chunk-1"]
    assert result["fused_results"][0]["text"] == "Jordan works for Acme."
    assert result["fused_results"][0]["page_number"] == 4
    assert result["fused_results"][0]["page_numbers"] == [4, 5]


def test_graph_only_hit_with_missing_chunk_is_dropped() -> None:
    neo4j = GraphOnlyNeo4j([])
    service = HybridQueryService(
        qdrant=EmptyQdrant(),
        neo4j=neo4j,
        embedder=EmbeddingService(force_fallback=True),
    )

    result = asyncio.run(service.search("Who is Jordan?"))

    assert neo4j.requested_chunk_ids == ["chunk-1"]
    assert result["fused_results"] == []
