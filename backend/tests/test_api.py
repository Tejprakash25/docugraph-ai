import fitz
from fastapi.testclient import TestClient

from main import app


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
