# DocuGraph AI — Product Requirements Document

## Version and status

- Version: 1.2
- Updated: 2026-11-01
- Product status: Backend Phases 1–5 complete; Frontend Phase 6 pending
- Supersedes: `DocuGraph_AI_PRD_v1.1.pdf` for implementation-status tracking
- Data status: The repository includes fictional sample contracts for testing only

## 1. Product overview

DocuGraph AI is a document-intelligence system that converts PDF documents into
searchable text chunks, entities, relationships, embeddings, and citation-backed
answers. It combines vector retrieval from Qdrant with graph retrieval from Neo4j
and synthesizes a concise answer through an LLM when available.

The product must help a user ask natural-language questions about indexed
documents without requiring the user to understand vector search, Cypher, graph
schemas, chunking, or embedding details.

## 2. Product goals

1. Ingest PDF documents reliably and preserve page-aware source metadata.
2. Extract entities and relationships with confidence values.
3. Support both semantic document search and relationship-oriented graph search.
4. Fuse retrieval signals into a ranked evidence set.
5. Return concise answers with validated chunk citations and page numbers.
6. Keep detailed retrieval and quality signals available for the future frontend's
   citations, graph, and metrics views.
7. Avoid exposing an entire document as the normal user-facing answer.

## 3. Implemented capabilities

### Phase 1 — Foundation: complete

- FastAPI application skeleton
- Environment-based configuration
- Docker Compose services for FastAPI, Neo4j, and Qdrant
- `/health` endpoint with service status

### Phase 2 — Ingestion: complete

- PDF parsing with PyMuPDF
- Page-aware chunking with the planned token-window behavior
- LLM extraction with Groq primary, Gemini fallback, and deterministic local fallback
- Entity and relationship confidence scoring
- Upload validation and `POST /ingest`

### Phase 3 — Indexing: complete

- Entity and relationship persistence in Neo4j
- Embedding and chunk persistence in Qdrant
- Document and chunk metadata, including page information
- `GET /documents/{document_id}/stats`
- Health reporting for LLM mode, Neo4j, and Qdrant connectivity

### Phase 4 — Query processing: complete

- Bounded vector retrieval
- Safe natural-language query planning
- Parameterized graph search; user text is not executed as Cypher
- Vector/graph result fusion and ranking
- Document filtering and bounded result parameters

### Phase 5 — Synthesis: complete

- LLM answer synthesis through Groq and Gemini providers
- Deterministic fallback when providers are unavailable
- `[chunk_id]` citation parsing and retrieved-chunk allowlisting
- Citation page lookup and bounded excerpts
- Confidence and citation-coverage annotations
- Concise relationship fallback answers for supported graph questions
- Public response redaction so normal vector/fused results do not return full chunk text

## 4. User-facing query behavior

The normal query response provides:

- A concise answer
- Validated citations
- Citation pages and bounded excerpts
- Confidence and citation coverage
- Provider information
- Compact retrieval, graph, fusion, and query-plan metadata for frontend views

The frontend will distribute this information into separate answer, citation,
graph, and metrics sections. Retrieval metadata is not intended to replace the
answer or display an entire contract by default.

## 5. Planned capabilities

### Phase 6 — Frontend: pending

- React + Vite + Tailwind application
- Query form and document selection
- Answer display with confidence annotation
- Citation panel with page references
- vis.js relationship graph
- Retrieval and ingestion metrics page
- Loading, empty, degraded-service, and error states

### Phase 7 — Integration and ship: pending

- End-to-end API/frontend tests
- 50-question benchmark
- Latency, throughput, and retrieval-quality improvements
- Production configuration and deployment
- Backend deployment to Railway
- Frontend deployment to Vercel

## 6. Non-functional requirements

- Keep document content bounded in user-facing responses.
- Do not log secrets or full sensitive document content.
- Validate document IDs, file types, upload sizes, query sizes, and result limits.
- Keep graph queries parameterized and limited to approved query templates.
- Report degraded service when a dependency is unavailable.
- Preserve source page and chunk identifiers for auditability.
- Use fictional sample contracts only for local development and testing.

## 7. Known limitations before release

- Confidence is a retrieval-and-citation heuristic, not a calibrated probability.
- Citation coverage measures citation usage against retrieved evidence; it does not
  independently prove factual correctness.
- Provider token usage, latency, and cost metrics are not yet exposed.
- Broad benchmark coverage and end-to-end frontend validation are still pending.
- Production authentication, authorization, rate limiting, and deployment controls
  remain release-hardening work.

## 8. Acceptance status

The backend implementation satisfies the planned Phase 1–5 scope. Phase 5 is
ready for frontend integration. The product is not considered fully shipped until
Phases 6 and 7 are completed and the benchmark and deployment checks pass.
