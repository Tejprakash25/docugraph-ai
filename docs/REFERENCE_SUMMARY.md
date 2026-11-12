# DocuGraph AI — Reference Summary

This summary records the project guidance across all document revisions.
It preserves the original plan alongside every later revision so you can see
exactly where the implementation diverged, expanded, or compromised.

## Document inventory

| Document | Version | Date | Purpose |
|---|---|---|---|
| [DocuGraph_AI_PRD_v1.1.pdf](./DocuGraph_AI_PRD_v1.1.pdf) | 1.1 | — | Original product vision and MVP scope |
| [DocuGraph_AI_SRS_v1.1.pdf](./DocuGraph_AI_SRS_v1.1.pdf) | 1.1 | — | Original system requirements and quality gates |
| [DocuGraph_AI_PRD_v1.2.md](./DocuGraph_AI_PRD_v1.2.md) | 1.2 | — | Refined PRD after Phases 1–4 implementation |
| [DocuGraph_AI_SRS_v1.2.md](./DocuGraph_AI_SRS_v1.2.md) | 1.2 | — | Refined SRS after Phases 1–4 implementation |
| [DocuGraph_AI_PRD_v1.3.md](./DocuGraph_AI_PRD_v1.3.md) | 1.3 | 2026-11-09 | Current PRD — adds RRP rethinking, retrieval hardening, known limitations |
| [DocuGraph_AI_SRS_v1.3.md](./DocuGraph_AI_SRS_v1.3.md) | 1.3 | 2026-11-09 | Current SRS — adds 3-hop search, typed entity linking, rethinking spec, frontend contract |

Phases 1–5 of the backend are implemented and tested. Phase 6 (frontend) is in
early boilerplate. Phase 7 (integration, benchmark, deployment) has not started.

## Product direction (from v1.1, still valid)

DocuGraph AI is intended to be an auditable document-intelligence system. Its answers should explain why they were produced and allow users to verify them against source chunks, page numbers, graph paths, and confidence scores.

The core architecture combines:

- Qdrant for semantic vector search over document chunks.
- Neo4j for structured relationship reasoning and multi-hop graph search.
- An LLM layer for extraction and answer synthesis, with Groq as primary and Gemini as fallback.

## MVP scope

The MVP includes:

1. FastAPI foundation and local Docker Compose setup.
2. PDF parsing and chunking with PyMuPDF.
3. LLM-based entity and relationship extraction with confidence scoring.
4. Neo4j triplet storage and Qdrant vector indexing.
5. Hybrid vector-plus-graph query processing.
6. LLM answer synthesis with inline citations.
7. React/Vite frontend with graph, citation, and metrics views.
8. End-to-end testing, benchmark evaluation, and Railway/Vercel deployment.

Explicitly outside the MVP are multi-document reasoning, fine-tuned extraction models, temporal reasoning, cross-document link analysis, conversation history, authentication, and multi-tenancy.

## Important functional requirements

- Uploaded PDFs should be processed in memory and not persisted as original files.
- Only extracted data should be persisted to Neo4j and Qdrant.
- Answers need source citations containing chunk and page information.
- Extracted relationships need confidence scores.
- The query path should combine vector retrieval and graph retrieval.
- LLM-generated Cypher must be validated as read-only before execution. It must not be allowed to create, modify, or delete graph data.
- The system should degrade gracefully when Groq, Gemini, Neo4j, or Qdrant is unavailable.
- LLM failures should use retries/backoff and the defined fallback behavior.

## Targets and quality gates

The documents describe these as targets, not achieved results:

- Factual accuracy: 94% target, with 85% minimum acceptance floor.
- Citation coverage: 98% target.
- Query latency: under 2 seconds on 500-page documents.
- Ingestion: approximately 8–10 seconds per 100 pages for the MVP.
- Extraction coverage: 90% or higher.
- Average relationship confidence: 0.85 or higher.
- Approximately 100 concurrent users for the single-instance MVP.
- A 50-question benchmark across 10 documents is required before claiming accuracy.

## Security and operational constraints

- API keys belong only in `.env` or platform secret storage.
- Original PDFs should not be stored.
- Structured JSON logging should record query counts and latency without logging sensitive document content.
- CORS must be restricted before deployment.
- The current MVP goal is free-tier/self-hosted operation with zero running cost.
- Future work includes audit trails, encryption at rest, and 30-day retention controls.

## Dependency guidance for later implementation

The SRS identifies these future dependencies by phase:

- PyMuPDF and `python-multipart` for ingestion.
- `sentence-transformers` for embeddings.
- `qdrant-client` for vector indexing.
- `neo4j` for graph access.
- `groq` and `google-genai` for LLM access.
- `python-json-logger` for structured logs.
- spaCy only if the fallback extraction path is retained.

Dependency versions must be verified at installation time. In particular, the reference notes that the old `qdrant-client==2.7.0` pin is invalid and should not be copied blindly.

## Current alignment

The repository has completed Phases 1–5: FastAPI foundation, PDF ingestion and extraction, Neo4j/Qdrant indexing, document statistics, connectivity-aware health reporting, safe hybrid vector/graph query processing, and auditable answer synthesis with citations. Phases 6–7 remain planned.

## Approval gate

This reference summary is saved for review. No code, dependency, Docker, environment, or infrastructure changes should begin until the plan and these references are approved.
