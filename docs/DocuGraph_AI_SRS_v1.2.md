# DocuGraph AI — Software Requirements Specification

## Version and implementation status

- Version: 1.2
- Updated: 2026-11-01
- Implementation status: Phases 1–5 complete
- Next implementation stage: Phase 6 frontend
- Reference baseline: `DocuGraph_AI_SRS_v1.1.pdf`

## 1. System architecture

The backend is a FastAPI service running with Docker Compose alongside:

- Neo4j for entities, relationships, and graph traversal
- Qdrant for chunk embeddings and vector similarity search
- Groq and Gemini as optional LLM providers
- A deterministic local fallback for extraction and synthesis

The processing path is:

`PDF upload → parse → page-aware chunks → extraction → embeddings → Neo4j/Qdrant → hybrid retrieval → synthesis → validated response`

## 2. Functional requirements and status

| ID | Requirement | Status |
|---|---|---|
| FR-01 | Accept a validated PDF upload with a document ID | Complete |
| FR-02 | Extract page-aware text chunks | Complete |
| FR-03 | Extract entities and relationships with confidence values | Complete |
| FR-04 | Persist graph data in Neo4j | Complete |
| FR-05 | Persist embeddings and metadata in Qdrant | Complete |
| FR-06 | Report document extraction statistics | Complete |
| FR-07 | Report dependency-aware health status | Complete |
| FR-08 | Run bounded vector retrieval | Complete |
| FR-09 | Run safe parameterized graph retrieval | Complete |
| FR-10 | Fuse and rank vector and graph evidence | Complete |
| FR-11 | Generate an answer from retrieved evidence | Complete |
| FR-12 | Validate and resolve `[chunk_id]` citations | Complete |
| FR-13 | Return page references, confidence, and citation coverage | Complete |
| FR-14 | Prevent full source chunks from normal public retrieval arrays | Complete |
| FR-15 | Render answer, citations, graph, and metrics in a web frontend | Pending — Phase 6 |
| FR-16 | Validate the complete product with benchmark and deployment tests | Pending — Phase 7 |

## 3. API requirements

### `GET /health`

Returns overall service state and the status of the LLM mode, Neo4j, and Qdrant.
The service is `healthy` only when required dependencies are connected; otherwise
it reports `degraded` with dependency-level status.

### `POST /ingest`

Accepts a PDF upload and a validated `document_id`. Returns chunk count, entity
count, relationship count, average extraction confidence, page count, and
processing time.

### `GET /documents/{document_id}/stats`

Returns entity counts by type, average confidence by type, relationship counts by
predicate, and an overall extraction-quality score.

### `POST /query`

Accepts a natural-language query with optional document ID, top-k limit, graph
limit, and maximum graph hops. Returns:

- `answer`
- `citations`
- `confidence`
- `synthesis_provider`
- `citation_coverage`
- compact `vector_results`
- compact `graph_results`
- compact `fused_results`
- `query_plan`

Full chunk text is used internally for synthesis and citation resolution but is
not returned in the normal vector or fused result arrays. Citation excerpts and
graph evidence previews are bounded.

## 4. Synthesis and citation requirements

1. The synthesis prompt must treat retrieved document content as untrusted data.
2. The answer must be generated only from the supplied retrieval context.
3. Providers must cite material claims with exact retrieved chunk IDs.
4. Citations not present in the current retrieval result set must be removed.
5. Citation records must include document ID, page information, bounded excerpt,
   and retrieval score when available.
6. If providers fail, the deterministic fallback must return a bounded answer and
   must not echo an entire retrieved document.
7. Confidence must remain within the inclusive range 0.0–1.0.

## 5. Security requirements

- Use environment variables for provider keys and database credentials.
- Do not commit `.env` secrets.
- Validate file extension, upload size, document ID, query length, and retrieval
  limits.
- Use fixed parameterized Cypher templates; never execute user-supplied Cypher.
- Keep provider prompts explicit about untrusted evidence and instruction
  injection.
- Avoid logging complete document contents in normal request handling.
- Keep public responses bounded to reduce accidental data exposure.
- Perform dependency and vulnerability checks before production deployment.

## 6. Quality and testing status

The backend contains automated coverage for ingestion, extraction validation,
indexing behavior, query planning, retrieval fusion, API behavior, citation
allowlisting, page resolution, fallback synthesis, response redaction, and
relationship fallback answers.

The following remain planned validation work:

- Full end-to-end ingestion-to-query tests across all sample contracts
- Frontend component and browser-flow tests
- 50-question retrieval and answer benchmark
- Latency and concurrent-user testing
- Production deployment smoke tests

## 7. Frontend integration contract

The frontend should treat `answer` as the primary user-facing output. It should
display citations separately, use `chunk_id` and pages for source navigation,
render graph results as relationships, and use retrieval scores and confidence
for metrics or diagnostic views. It should not reconstruct or display hidden full
chunk text from backend internals.

## 8. Release criteria

The system may enter frontend implementation now because the backend Phase 1–5
contract is implemented. A production release requires completion of Phase 6 and
Phase 7, including authentication and deployment controls, benchmark results,
security review, performance checks, and successful end-to-end verification.
