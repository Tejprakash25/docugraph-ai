# DocuGraph AI — Project Plan

## Phase 1 ✅ DONE: Foundation

- FastAPI skeleton
- Environment configuration
- Docker Compose with FastAPI, Neo4j, and Qdrant
- `/health` endpoint

## Phase 2 ✅ DONE: Ingestion

- PDF parsing with PyMuPDF
- Document chunking: 300–500 tokens with 50-token overlap
- LLM entity and relationship extraction
- Confidence scoring
- `POST /ingest` endpoint

Implemented with PyMuPDF, page-aware token windows, confidence-scored extraction,
Groq → Gemini → local fallback behavior, upload validation, and automated tests.

## Phase 3 ✅ DONE: Indexing

- Store extracted triplets in Neo4j
- Store embeddings in Qdrant
- Store document and chunk metadata
- `/documents/{id}/stats` endpoint
- Full `/health` endpoint with database connectivity checks

Implemented with Neo4j graph persistence, Qdrant vector persistence, 384-dimensional
embeddings with a deterministic offline fallback, document quality statistics, and
degraded-service health reporting.

## Phase 4 ✅ DONE: Query Processing

- Vector search
- Natural-language-to-Cypher translation
- Graph search
- Search fusion and ranking

Implemented with bounded Qdrant retrieval, parameterized Neo4j graph search,
safe natural-language query planning, and weighted vector/graph fusion.

## Phase 5: Synthesis

- LLM-generated answers
- `[chunk_id]` citation parsing
- Page lookup for citations
- Confidence annotation

## Phase 6: Frontend

- React + Vite + Tailwind
- Query form
- Answer display
- vis.js graph visualization
- Citation panel
- Metrics page

## Phase 7: Integration and Ship

- End-to-end tests
- 50-question benchmark
- Performance improvements
- Deploy backend to Railway
- Deploy frontend to Vercel

## Current Status

Phases 1, 2, 3, and 4 are complete. Phase 5 — answer synthesis and citations — is next.
