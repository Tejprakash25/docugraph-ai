import fitz
from fastapi.testclient import TestClient

from main import app
from api.routes import (
    _public_query_result,
    get_indexing_service,
    get_ingestion_service,
    get_query_service,
    get_synthesis_service,
)
from services.ingest import PdfIngestionService
from services.synthesis import SynthesisService


app.dependency_overrides[get_ingestion_service] = lambda: PdfIngestionService()


class FakeIndexing:
    def get_document_stats(self, document_id: str):
        return {
            "document_id": document_id,
            "status": "indexed",
            "extraction_quality": {
                "entities_by_type": {"Person": 2},
                "avg_confidence_by_type": {"Person": 0.9},
                "relationships_by_predicate": {"signs": 1},
                "overall_quality_score": 0.9,
            },
        }

    def health(self):
        return {"neo4j": "connected", "qdrant": "connected"}


def make_pdf(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_ingest_endpoint_returns_phase_two_contract() -> None:
    client = TestClient(app)
    response = client.post(
        "/ingest",
        data={"document_id": "contract_001", "document_type": "contract"},
        files={"file": ("contract.pdf", make_pdf("Alice signs Acme Corp."), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["document_id"] == "contract_001"
    assert body["chunks_created"] == 1
    assert body["pages"] == 1
    assert body["entities_extracted"] >= 2
    assert body["relationships_extracted"] >= 1
    assert 0 <= body["avg_confidence"] <= 1


def test_ingest_endpoint_rejects_path_traversal_document_id() -> None:
    client = TestClient(app)
    response = client.post(
        "/ingest",
        data={"document_id": "../secrets"},
        files={"file": ("contract.pdf", make_pdf("text"), "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["status"] == "error"
    assert response.json()["error"] == "document_id must contain only letters, numbers, underscores, and hyphens"


def test_document_stats_endpoint_returns_extraction_quality() -> None:
    app.dependency_overrides[get_indexing_service] = lambda: FakeIndexing()
    client = TestClient(app)

    response = client.get("/documents/contract_001/stats")

    assert response.status_code == 200
    assert response.json()["status"] == "indexed"
    assert response.json()["extraction_quality"]["overall_quality_score"] == 0.9


def test_health_reports_storage_connectivity(monkeypatch) -> None:
    import main

    monkeypatch.setattr(main, "get_indexing_service", lambda: FakeIndexing())
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["services"]["neo4j"] == "connected"
    assert response.json()["services"]["qdrant"] == "connected"


def test_query_endpoint_returns_hybrid_contract() -> None:
    class FakeQuery:
        async def search(self, query, **kwargs):
            return {
                "query": query,
                "vector_results": [],
                "graph_results": [],
                "fused_results": [],
                "query_plan": {"translator": "safe_parameterized_template", "entity_terms": [], "confidence": 0.75},
            }

    app.dependency_overrides[get_query_service] = lambda: FakeQuery()
    app.dependency_overrides[get_synthesis_service] = lambda: SynthesisService(providers=[])
    client = TestClient(app)
    response = client.post("/query", json={"query": "Who signed the contract?"})

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["query_plan"]["translator"] == "safe_parameterized_template"
    app.dependency_overrides.pop(get_query_service, None)
    app.dependency_overrides.pop(get_synthesis_service, None)


def test_query_endpoint_rejects_path_traversal_document_id() -> None:
    client = TestClient(app)
    response = client.post("/query", json={"query": "find data", "document_id": "../secrets"})

    assert response.status_code == 422
    assert response.json()["status"] == "error"


def test_public_query_result_does_not_expose_full_chunk_text() -> None:
    result = _public_query_result(
        {
            "query": "find it",
            "vector_results": [{"chunk_id": "chunk_1", "text": "x" * 2000, "score": 0.9}],
            "graph_results": [{"chunk_ids": ["chunk_1"], "evidence": "y" * 2000, "score": 0.8}],
            "fused_results": [{"chunk_id": "chunk_1", "text": "z" * 2000, "score": 0.9}],
            "query_plan": {},
        }
    )

    assert "text" not in result["vector_results"][0]
    assert "text_preview" not in result["vector_results"][0]
    assert "evidence" not in result["graph_results"][0]
    assert len(result["graph_results"][0]["evidence_preview"]) == 240
