import fitz
import pytest

from services.ingest import IngestionError, PdfIngestionService, parse_pdf


def make_pdf(*pages: str) -> bytes:
    document = fitz.open()
    for page_text in pages:
        page = document.new_page()
        page.insert_text((72, 72), page_text)
    content = document.tobytes()
    document.close()
    return content


def test_parse_pdf_preserves_page_metadata_and_offsets() -> None:
    parsed = parse_pdf(
        make_pdf("Alice signs the contract.", "Acme pays Alice 100 dollars."),
        document_id="contract_001",
        filename="contract.pdf",
    )

    assert parsed.page_count == 2
    assert len(parsed.chunks) == 1
    assert parsed.chunks[0].document_id == "contract_001"
    assert parsed.chunks[0].page_number == 1
    assert parsed.chunks[0].page_numbers == [1, 2]
    assert parsed.chunks[0].start_offset == 0
    assert parsed.chunks[0].end_offset > parsed.chunks[0].start_offset
    assert "Acme pays Alice" in parsed.chunks[0].text


def test_parse_pdf_creates_overlapping_token_windows() -> None:
    parsed = parse_pdf(
        make_pdf(
            *(" ".join(f"token{i}" for i in range(start, start + 20)) for start in range(0, 200, 20)),
        ),
        document_id="long_doc",
        filename="long.pdf",
        chunk_size_tokens=40,
        chunk_overlap_tokens=10,
    )

    assert len(parsed.chunks) == 4
    assert all(1 <= chunk.token_count <= 40 for chunk in parsed.chunks)
    assert parsed.chunks[0].text.split()[-10:] == parsed.chunks[1].text.split()[:10]


def test_parse_pdf_rejects_non_pdf_content() -> None:
    with pytest.raises(IngestionError, match="valid PDF"):
        parse_pdf(b"not a pdf", document_id="doc1", filename="doc.txt")


def test_ingestion_service_returns_phase_two_summary() -> None:
    service = PdfIngestionService()
    result = service.ingest_bytes(
        make_pdf("Alice signs Acme Corp."),
        document_id="contract_001",
        filename="contract.pdf",
    )

    assert result.document_id == "contract_001"
    assert result.pages == 1
    assert result.chunks_created == 1
    assert result.entities_extracted >= 2
    assert result.relationships_extracted >= 1
    assert 0 <= result.avg_confidence <= 1
    assert result.processing_time_seconds >= 0
