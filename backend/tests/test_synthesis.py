import asyncio
import logging

from services.synthesis import (
    CitationResolver,
    DeterministicAnswerProvider,
    SynthesisService,
)


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


def test_fallback_returns_relevant_sentence_with_citation_not_chunk_dump() -> None:
    context = (
        "[contract_001_chunk_2] pages=[2, 3]: "
        "Northstar will pay Cedar Finch an implementation fee of USD 48,500 "
        "and a support fee of USD 6,200 per month during the first twelve months. "
        "Neither Party may charge expenses without prior written approval."
    )

    answer = asyncio.run(
        DeterministicAnswerProvider().generate(
            "What is Northstar's monthly support fee?",
            context,
        )
    )

    assert answer == (
        "Northstar will pay Cedar Finch an implementation fee of USD 48,500 "
        "and a support fee of USD 6,200 per month during the first twelve months. "
        "[contract_001_chunk_2]"
    )
    assert "prior written approval" not in answer


def test_fallback_can_use_relevant_sentence_past_old_chunk_limit() -> None:
    relevant_sentence = "The fictional standard lead time is twenty-one days after confirmation."
    retrieval = {
        "vector_results": [],
        "graph_results": [],
        "fused_results": [
            {
                "chunk_id": "contract_004_chunk_1",
                "document_id": "contract_004",
                "page_number": 1,
                "page_numbers": [1],
                "text": ("Earlier contract details. " * 80) + relevant_sentence,
                "score": 0.9,
            },
            {
                "chunk_id": "contract_004_chunk_2",
                "document_id": "contract_004",
                "page_number": 2,
                "page_numbers": [1, 2],
                "text": "Marble Kite will invoice after shipment and Cobalt River will pay undisputed invoices within forty-five days.",
                "score": 0.8,
            },
        ],
    }

    result = asyncio.run(
        SynthesisService(providers=[]).synthesize(
            "How many days after order confirmation is Marble Kite's standard lead time?",
            retrieval,
        )
    )

    assert result.answer == f"{relevant_sentence} [contract_004_chunk_1]"
    assert result.citations[0].chunk_id == "contract_004_chunk_1"


def test_fallback_calculates_service_credit_from_retrieved_facts() -> None:
    retrieval = {
        "vector_results": [],
        "graph_results": [],
        "fused_results": [
            {
                "chunk_id": "contract_002_chunk_2",
                "document_id": "contract_002",
                "page_number": 2,
                "page_numbers": [2, 3],
                "text": (
                    "Blue Oak will pay a monthly operations fee of USD 4,850, and variable cloud "
                    "costs capped at USD 2,000 per month. If monthly availability falls below 99.5% "
                    "because of a Lumen Harbor-controlled failure, Blue Oak may receive a service "
                    "credit of five percent of the monthly operations fee."
                ),
                "score": 0.9,
            }
        ],
    }

    result = asyncio.run(
        SynthesisService(providers=[]).synthesize(
            "If monthly availability is 99.4% due to a Lumen Harbor-controlled failure, what service credit may Blue Oak receive, how much is that based on the monthly operations fee, and is the cloud-cost cap part of the calculation?",
            retrieval,
        )
    )

    assert result.provider == "fallback"
    assert result.answer == (
        "At 99.4% availability, below the 99.5% threshold, the potential service credit is 5%: "
        "5% of the USD 4,850.00 monthly operations fee is USD 242.50. "
        "The USD 2,000.00 monthly cloud-cost cap is separate and is not part of the calculation. "
        "[contract_002_chunk_2]"
    )
    assert [citation.chunk_id for citation in result.citations] == ["contract_002_chunk_2"]


def test_fallback_does_not_guess_missing_cloud_cost_cap() -> None:
    answer = asyncio.run(
        DeterministicAnswerProvider().generate(
            "How much is the service credit based on the monthly operations fee, and is the cloud-cost cap part of the calculation?",
            "[contract_002_chunk_2] pages=[2, 3]: The monthly operations fee of USD 4,850 applies. "
            "The service credit is five percent of the monthly operations fee.",
        )
    )

    assert answer == (
        "I could not determine whether the cloud-cost cap is separate because the retrieved evidence does not state that cap."
    )


def test_failed_primary_provider_is_logged_and_fallback_provider_is_tried(caplog) -> None:
    class FailedProvider:
        name = "primary"

        async def generate(self, question: str, context: str) -> str:
            raise RuntimeError("provider unavailable")

    provider = FakeProvider()
    result = asyncio.run(
        SynthesisService(providers=[FailedProvider(), provider]).synthesize(
            "Who signed?",
            retrieval_fixture(),
        )
    )

    assert result.provider == "test-provider"
    assert "Answer provider primary failed (RuntimeError)" in caplog.text
    assert "provider unavailable" not in caplog.text


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
