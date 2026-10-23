import asyncio

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

