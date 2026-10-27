import asyncio

from services.synthesis import CitationResolver, SynthesisService


class FakeProvider:
    name = "test-provider"

    async def generate(self, question: str, context: str) -> str:
        assert question == "Who signed?"
        assert "contract_001_chunk_1" in context
        return "Alice signed the agreement. [contract_001_chunk_1] [not_retrieved]"


def retrieval_fixture() -> dict:
    return {
        "vector_results": [
            {
                "chunk_id": "contract_001_chunk_1",
                "document_id": "contract_001",
                "page_number": 3,
                "page_numbers": [3],
                "text": "Alice signed the agreement with Acme Corp.",
                "score": 0.92,
            }
        ],
        "graph_results": [],
        "fused_results": [
            {
                "chunk_id": "contract_001_chunk_1",
                "document_id": "contract_001",
                "page_number": 3,
                "page_numbers": [3],
                "text": "Alice signed the agreement with Acme Corp.",
                "score": 0.92,
            }
        ],
    }


def test_synthesis_resolves_pages_and_removes_unverified_citations() -> None:
    service = SynthesisService(providers=[FakeProvider()])
    result = asyncio.run(service.synthesize("Who signed?", retrieval_fixture()))

    assert result.provider == "test-provider"
    assert result.answer == "Alice signed the agreement. [contract_001_chunk_1]"
    assert result.citations[0].chunk_id == "contract_001_chunk_1"
    assert result.citations[0].pages == [3]
    assert result.citation_coverage == 1.0
    assert 0 < result.confidence <= 1


def test_fallback_synthesis_is_citable_without_provider_keys() -> None:
    result = asyncio.run(SynthesisService(providers=[]).synthesize("Who signed?", retrieval_fixture()))

    assert result.provider == "fallback"
    assert "contract_001_chunk_1" in result.answer
    assert len(result.answer) <= 380
    assert result.citations[0].pages == [3]


def test_citation_resolver_ignores_unknown_chunk_ids() -> None:
    citations, coverage = CitationResolver().resolve(
        "Answer [known_chunk] [unknown_chunk]",
        {
            "vector_results": [{"chunk_id": "known_chunk", "page_number": 2, "text": "evidence", "score": 0.8}],
            "fused_results": [],
            "graph_results": [],
        },
    )

    assert [citation.chunk_id for citation in citations] == ["known_chunk"]
    assert coverage == 1.0


def test_fallback_answers_work_for_relationship_without_echoing_chunk_text() -> None:
    retrieval = retrieval_fixture()
    retrieval["graph_results"] = [
        {
            "source": "Acme Corp",
            "source_type": "Organization",
            "predicate": "works_for",
            "target": "Alice",
            "target_type": "Person",
            "chunk_ids": ["contract_001_chunk_1"],
            "score": 0.9,
        }
    ]

    result = asyncio.run(
        SynthesisService(providers=[]).synthesize("Who works for Acme Corp?", retrieval)
    )

    assert result.answer == "Alice works for Acme Corp. [contract_001_chunk_1]"
    assert result.citations[0].chunk_id == "contract_001_chunk_1"
