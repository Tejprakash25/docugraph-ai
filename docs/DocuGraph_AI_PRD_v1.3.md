# DocuGraph AI - Product Requirements Document

## Version and status

- Version: 1.3
- Updated: 2026-11-09
- Product status: Backend Phases 1-5 complete with retrieval hardening and RRP-inspired rethinking; Frontend Phase 6 pending
- Supersedes: `DocuGraph_AI_PRD_v1.2.md`
- Data status: The repository includes fictional sample contracts for testing only

## 1. Product overview

DocuGraph AI is a document-intelligence system that converts PDF documents into
searchable text chunks, entities, relationships, embeddings, and citation-backed
answers. It combines vector retrieval from Qdrant with multi-hop graph retrieval
from Neo4j, ranks the combined evidence through a reasoning-path rethinking step,
and synthesizes a concise answer through an LLM when available.

The product must help a user ask natural-language questions about indexed
documents without requiring the user to understand vector search, Cypher, graph
schemas, chunking, or embedding details.

## 2. Research basis

- Base paper: Reliable Reasoning Path: Distilling Effective Guidance for LLM
  Reasoning with Knowledge Graphs (IEEE TKDE, 2026). Adapted idea: score,
  filter, and rank reasoning paths before answer generation.
- Building Multimodal Knowledge Graphs: Automation for Enterprise Integration
  (IEEE Internet Computing, 2025). Used for automated graph construction with provenance.
- CoTPR: Chain-of-Thought-Enhanced Path Planning and Retrieval for Faithful
  Knowledge Graph Question Answering (IEEE IoT Journal, 2026). Used for bounded
  multi-hop path retrieval.
- Unifying Large Language Models and Knowledge Graphs: A Roadmap (IEEE TKDE, 2024).
  Used for theory and positioning.

## 3. Product goals

1. Ingest PDF documents reliably and preserve page-aware source metadata.
2. Extract entities and relationships with confidence values.
3. Support both semantic document search and relationship-oriented multi-hop graph search.
4. Rank combined evidence through reasoning-path scoring and filtering.
5. Return concise answers with validated chunk citations and page numbers.
6. Never link entities by guesswork; prefer a missing link over a wrong one.
7. Keep detailed retrieval and quality signals available for the future frontend's
   citations, graph, and metrics views.
8. Avoid exposing an entire document as the normal user-facing answer.

## 4. Implemented capabilities

### Phase 1 - Foundation: complete

- FastAPI application skeleton
- Environment-based configuration
- Docker Compose services for FastAPI, Neo4j, and Qdrant
- `/health` endpoint with service status

### Phase 2 - Ingestion: complete

- PDF parsing with PyMuPDF
- Page-aware chunking with the planned token-window behavior
- LLM extraction with Groq primary, Gemini fallback, and deterministic local fallback
- Entity and relationship confidence scoring
- Upload validation and `POST /ingest`

### Phase 3 - Indexing: complete

- Entity and relationship persistence in Neo4j
- Relationship endpoints matched by entity name and type within the same document
- Ambiguous or untyped relationships skipped and logged instead of guessed
- Embedding and chunk persistence in Qdrant
- Document and chunk metadata, including page information
- `GET /documents/{document_id}/stats`
- Health reporting for LLM mode, Neo4j, and Qdrant connectivity

### Phase 4 - Query processing: complete

- Bounded vector retrieval
- Safe natural-language query planning
- Parameterized graph search up to 3 hops; user text is not executed as Cypher
- Ordered multi-hop paths with hop count and provenance chunk IDs
- Hydration of graph-only evidence with chunk text and pages
- RRP-inspired rethinking: semantic and structural path scoring, threshold
  filtering, ranking, and vector-only fallback
- Document filtering and bounded result parameters

### Phase 5 - Synthesis: complete

- LLM answer synthesis through Groq (primary) and Gemini (fallback)
- Deterministic fallback when providers are unavailable
- `[chunk_id]` citation parsing and retrieved-chunk allowlisting
- Citation page lookup and bounded excerpts
- Confidence and citation-coverage annotations
- Concise relationship fallback answers for supported graph questions
- Public response redaction so normal vector/fused results do not return full chunk text

## 5. User-facing query behavior

The normal query response provides:

- A concise answer
- Validated citations
- Citation pages and bounded excerpts
- Confidence and citation coverage
- Provider information
- Compact retrieval, graph, ranked-evidence, and query-plan metadata for frontend views

The frontend will distribute this information into separate answer, citation,
graph, and metrics sections. Retrieval metadata is not intended to replace the
answer or display an entire contract by default.

## 6. Planned capabilities

### Phase 6 - Frontend: pending

- React + Vite + TypeScript + Tailwind application
- Query form and document selection
- Answer display with confidence annotation
- Citation panel with page references
- vis.js relationship graph showing multi-hop paths
- Retrieval and ingestion metrics page
- Loading, empty, degraded-service, and error states

### Phase 7 - Integration and ship: pending

- End-to-end API/frontend tests
- 50-question benchmark comparing vector-only, graph-only, and hybrid with rethinking
- Tuning of rethinking weights and threshold from benchmark results
- Latency, throughput, and retrieval-quality improvements
- Production configuration and deployment
- Backend deployment to Railway
- Frontend deployment to Vercel

## 7. Non-functional requirements

- Keep document content bounded in user-facing responses.
- Do not log secrets or full sensitive document content.
- Validate document IDs, file types, upload sizes, query sizes, and result limits.
- Keep graph queries parameterized and limited to approved query templates.
- Report degraded service when a dependency is unavailable.
- Preserve source page and chunk identifiers for auditability.
- Never return evidence rows with empty text or unknown pages.
- Pin infrastructure image versions for reproducible demos and deployments.
- Use fictional sample contracts only for local development and testing.

## 8. Known limitations before release

- Confidence is a retrieval-and-citation heuristic, not a calibrated probability.
- Citation coverage measures citation usage against retrieved evidence; it does not
  independently prove factual correctness.
- The semantic path score uses embedding similarity, not LLM-generated reasoning
  paths as in the base paper; upgrade is planned after the Phase 7 benchmark.
- Relationships between same-name entities of different types in one document are
  skipped until relationship types are added to extraction.
- Rethinking weights and threshold are defaults, not yet tuned on a benchmark.
- Provider token usage, latency, and cost metrics are not yet exposed.
- Broad benchmark coverage and end-to-end validation on live services are still pending.
- Production authentication, authorization, rate limiting, and deployment controls
  remain release-hardening work.

## 9. Acceptance status

The backend implementation satisfies the planned Phase 1-5 scope, including
type-safe graph linking, multi-hop provenance, evidence hydration, and the
rethinking step. The backend is ready for frontend integration. The product is
not considered fully shipped until Phases 6 and 7 are completed and the benchmark
and deployment checks pass.