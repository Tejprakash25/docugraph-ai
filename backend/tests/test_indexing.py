import asyncio

import fitz

from services.embedding import EmbeddingService
from services.extraction import Entity, ExtractionResult, Relationship
from services.indexing import IndexingService
from services.ingest import parse_pdf


def make_pdf(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


class FakeNeo4j:
    def __init__(self) -> None:
        self.documents = []
        self.entities = []
        self.relationships = []

    def upsert_document(self, **kwargs):
        self.documents.append(kwargs)

    def upsert_extractions(self, **kwargs):
        self.entities.extend(kwargs["entities"])
        self.relationships.extend(kwargs["relationships"])

    def get_document_stats(self, document_id):
        return {
            "document_id": document_id,
            "status": "indexed",
            "extraction_quality": {
                "entities_by_type": {"Person": 1},
                "avg_confidence_by_type": {"Person": 0.9},
                "relationships_by_predicate": {"signs": 1},
                "overall_quality_score": 0.9,
            },
        }

    def health(self):
        return True


class FakeQdrant:
    def __init__(self) -> None:
        self.points = []

    def upsert_chunks(self, **kwargs):
        self.points.extend(kwargs["points"])

    def health(self):
        return True


def test_embedding_fallback_is_deterministic_and_384_dimensions() -> None:
    embedder = EmbeddingService(force_fallback=True)
    first = asyncio.run(embedder.embed_texts(["Alice signs the contract."]))[0]
    second = asyncio.run(embedder.embed_texts(["Alice signs the contract."]))[0]

    assert len(first) == 384
    assert first == second
    assert abs(sum(value * value for value in first) - 1.0) < 0.0001


def test_indexing_service_writes_graph_and_vector_records() -> None:
    parsed = parse_pdf(make_pdf("Alice signs Acme Corp."), "contract_001", "contract.pdf")
    extractions = {
        parsed.chunks[0].chunk_id: ExtractionResult(
            entities=[Entity("Alice", "Person", 0.9), Entity("Acme Corp", "Organization", 0.95)],
            relationships=[Relationship("Alice", "signs", "Acme Corp", 0.8)],
            provider="test",
        )
    }
    neo4j = FakeNeo4j()
    qdrant = FakeQdrant()
    indexing = IndexingService(
        neo4j=neo4j,
        qdrant=qdrant,
        embedder=EmbeddingService(force_fallback=True),
    )

    result = asyncio.run(indexing.index_document("contract_001", parsed, extractions, "contract"))

    assert result.neo4j == "indexed"
    assert result.qdrant == "indexed"
    assert len(neo4j.documents) == 1
    assert len(neo4j.entities) == 2
    assert len(neo4j.relationships) == 1
    assert len(qdrant.points) == 1
    assert len(qdrant.points[0]["vector"]) == 384
