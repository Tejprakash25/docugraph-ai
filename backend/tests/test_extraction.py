import pytest

from services.extraction import (
    ExtractionResult,
    HeuristicExtractor,
    parse_extraction_payload,
)


def test_parse_extraction_payload_accepts_markdown_wrapped_json() -> None:
    result = parse_extraction_payload(
        """```json
        {"entities": [{"name": "Alice", "type": "Person", "confidence": 0.91}],
         "relationships": [{"source": "Alice", "predicate": "signs",
         "target": "Contract", "confidence": 0.83, "evidence": "Alice signs Contract"}]}
        ```"""
    )

    assert isinstance(result, ExtractionResult)
    assert result.entities[0].name == "Alice"
    assert result.relationships[0].confidence == 0.83


def test_parse_extraction_payload_clamps_confidence_and_drops_invalid_edges() -> None:
    result = parse_extraction_payload(
        {
            "entities": [
                {"name": "Alice", "type": "Person", "confidence": 1.7},
                {"name": "", "type": "Person", "confidence": 0.5},
            ],
            "relationships": [
                {"source": "Alice", "predicate": "signs", "target": "", "confidence": -1},
            ],
        }
    )

    assert len(result.entities) == 1
    assert result.entities[0].confidence == 1
    assert result.relationships == []


@pytest.mark.asyncio
async def test_heuristic_extractor_provides_local_fallback() -> None:
    extractor = HeuristicExtractor()
    result = await extractor.extract(
        "Alice signs Acme Corp. Acme pays Alice $100 on 2026-01-01."
    )

    assert {entity.name for entity in result.entities} >= {"Alice", "Acme Corp"}
    assert any(edge.predicate == "signs" for edge in result.relationships)
    assert all(0 <= entity.confidence <= 1 for entity in result.entities)
    assert all(0 <= edge.confidence <= 1 for edge in result.relationships)
