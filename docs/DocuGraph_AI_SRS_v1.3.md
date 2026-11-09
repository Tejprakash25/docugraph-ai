# DocuGraph AI - Software Requirements Specification

## Version and implementation status

- Version: 1.3
- Updated: 2026-11-09
- Implementation status: Phases 1-5 complete, with retrieval hardening and RRP-inspired rethinking
- Next implementation stage: Phase 6 frontend
- Supersedes: `DocuGraph_AI_SRS_v1.2.md`
- Reference baseline: `DocuGraph_AI_SRS_v1.1.pdf`

## Changes since v1.2

- Graph search supports up to 3 hops (default remains 2).
- Relationships are linked by entity name and type, scoped to the same document.
- Graph search returns ordered multi-hop paths with hop count and provenance chunk IDs.
- Graph-only evidence is hydrated with chunk text and pages before synthesis.
- Fixed 0.7/0.3 fusion replaced by an RRP-inspired rethinking and ranking step.
- Qdrant image pinned to a fixed version; CORS origins passed through Docker Compose.

## 1. System architecture

The backend is a FastAPI service running with Docker Compose alongside:

- Neo4j for entities, relationships, provenance, and graph traversal
- Qdrant for chunk embeddings and vector similarity search
- Groq as the primary LLM provider and Gemini as the fallback provider
- A deterministic local fallback for extraction and synthesis

The processing path is:

`PDF upload -> parse -> page-aware chunks -> extraction -> embeddings -> Neo4j/Qdrant -> vector + graph retrieval -> evidence hydration -> rethinking and ranking -> synthesis -> validated response`

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
| FR-09 | Run safe parameterized graph retrieval up to 3 hops | Complete |
| FR-10 | Rank vector and graph evidence through the rethinking step | Complete |
| FR-11 | Generate an answer from retrieved evidence | Complete |
| FR-12 | Validate and resolve `[chunk_id]` citations | Complete |
| FR-13 | Return page references, confidence, and citation coverage | Complete |
| FR-14 | Prevent full source chunks from normal public retrieval arrays | Complete |
| FR-15 | Render answer, citations, graph, and metrics in a web frontend | Pending - Phase 6 |
| FR-16 | Validate the complete product with benchmark and deployment tests | Pending - Phase 7 |
| FR-17 | Link relationship endpoints by entity name and type within the same document; skip ambiguous or untyped relationships | Complete |
| FR-18 | Return ordered multi-hop graph paths with hop count and provenance chunk IDs | Complete |
| FR-19 | Hydrate graph-only evidence with chunk text and pages; drop rows that cannot be resolved | Complete |
| FR-20 | Score, filter, and rank reasoning paths; fall back to vector-only ranking when all paths are filtered | Complete |

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
limit, and maximum graph hops (`max_hops`: default 2, minimum 1, maximum 3).
Returns:

- `answer`
- `citations`
- `confidence`
- `synthesis_provider`
- `citation_coverage`
- compact `vector_results`
- compact `graph_results`
- compact `fused_results` (now produced by the rethinking step; key name unchanged)
- `query_plan`

Full chunk text is used internally for synthesis and citation resolution but is
not returned in the normal vector or fused result arrays. Citation excerpts and
graph evidence previews are bounded. The response shape is unchanged from v1.2.

## 4. Graph and provenance requirements

1. Entities are stored with name and type.
2. A relationship is created only when both endpoint entities resolve to a single
   type within the same document and both are mentioned in that document's chunks.
3. Relationships with ambiguous or missing endpoint types are skipped and counted
   in a log line; the system must not guess an entity link.
4. Each relationship stores its source chunk IDs and source pages.
5. Graph search returns the full ordered path for every hit, its hop count, and
   provenance chunk IDs merged from relationship sources and chunk mentions
   (deduplicated, capped at 20).
6. Graph evidence chunks are fetched in one bounded, parameterized lookup
   (`Neo4jStore.get_chunks`, maximum 50 IDs).
7. Evidence rows that cannot be resolved to chunk text are dropped; no row with
   empty text or page 0 may reach synthesis.

## 5. Rethinking and ranking requirements

The rethinking step (`services/rethinking.py`) adapts the reasoning-path
filtering idea of the base paper (Reliable Reasoning Path, IEEE TKDE 2026).

For each graph path:

- `semantic_score` = cosine similarity between the query embedding and the
  embedding of the verbalized path (`A predicate B predicate C ...`), computed
  in one batched embedding call
- `structural_score` = product of edge confidences along the path divided by hop count
- `S = lambda_semantic * semantic_score + lambda_structural * structural_score`

Then:

1. Paths with `S < rethink_threshold` are discarded.
2. Remaining paths are sorted by `S` and limited to `rethink_max_paths`.
3. Each chunk is scored as `max(vector_score, best S of any kept path whose
   provenance includes the chunk)`.
4. Chunks are deduplicated by `chunk_id` and the top `top_k` are returned.
5. If every path is filtered out, ranking falls back to vector results only.
   The step must never return empty results when vector hits exist.

| Setting | Default |
|---|---|
| `RETHINK_LAMBDA_SEMANTIC` | 0.6 |
| `RETHINK_LAMBDA_STRUCTURAL` | 0.4 |
| `RETHINK_THRESHOLD` | 0.35 |
| `RETHINK_MAX_PATHS` | 10 |

Documented shortcut: the semantic path score uses embedding similarity rather
than LLM-generated reasoning paths as in RRP. Upgrade is planned after the
Phase 7 benchmark.

## 6. Synthesis and citation requirements

1. The synthesis prompt must treat retrieved document content as untrusted data.
2. The answer must be generated only from the supplied retrieval context.
3. Providers must cite material claims with exact retrieved chunk IDs.
4. Citations not present in the current retrieval result set must be removed.
5. Citation records must include document ID, page information, bounded excerpt,
   and retrieval score when available.
6. If providers fail, the deterministic fallback must return a bounded answer and
   must not echo an entire retrieved document.
7. Confidence must remain within the inclusive range 0.0-1.0.

## 7. Security requirements

- Use environment variables for provider keys and database credentials.
- Do not commit `.env` secrets.
- Validate file extension, upload size, document ID, query length, and retrieval
  limits.
- Use fixed parameterized Cypher templates; never execute user-supplied Cypher.
- Keep provider prompts explicit about untrusted evidence and instruction
  injection.
- Avoid logging complete document contents in normal request handling.
- Keep public responses bounded to reduce accidental data exposure.
- Allow browser access only from origins listed in `CORS_ALLOWED_ORIGINS`.
- Perform dependency and vulnerability checks before production deployment.

## 8. Deployment configuration

- Docker Compose services: FastAPI, Neo4j 5.10 Community, Qdrant (pinned image version).
- `CORS_ALLOWED_ORIGINS` is passed through to the FastAPI container
  (default `http://localhost:5173,http://localhost:3000`).
- The Qdrant server image version and the `qdrant-client` version in
  `backend/requirements.txt` must be kept compatible.

## 9. Quality and testing status

The backend contains automated coverage for ingestion, extraction validation,
indexing behavior, query planning, hop clamping, typed and document-scoped entity
linking, ambiguous relationship skipping, ordered multi-hop paths, chunk lookup
limits, evidence hydration, missing-chunk removal, rethinking filters, path
promotion, vector fallback, API behavior, citation allowlisting, page resolution,
fallback synthesis, and response redaction.

The following remain planned validation work:

- Full end-to-end ingestion-to-query tests across all sample contracts on live Neo4j and Qdrant
- Frontend component and browser-flow tests
- 50-question retrieval and answer benchmark, including vector-only and graph-only baselines
- Latency and concurrent-user testing
- Production deployment smoke tests

## 10. Frontend integration contract

The frontend should treat `answer` as the primary user-facing output. It should
display citations separately, use `chunk_id` and pages for source navigation,
render graph results as relationships, and use retrieval scores and confidence
for metrics or diagnostic views. It should not reconstruct or display hidden full
chunk text from backend internals.

## 11. Release criteria

The system may enter frontend implementation now because the backend Phase 1-5
contract, including retrieval hardening and rethinking, is implemented. A
production release requires completion of Phase 6 and Phase 7, including
authentication and deployment controls, benchmark results, security review,
performance checks, and successful end-to-end verification.