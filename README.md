# DocuGraph AI

Hybrid document intelligence: vector search (Qdrant) + knowledge graph reasoning (Neo4j),
fused into auditable, citation-backed answers.

Full spec: see `DocuGraph_AI_Master_Build_Prompt.md`.

## Status: Phase 2 — Ingestion Complete

- [x] FastAPI skeleton
- [x] Config via pydantic-settings
- [x] Docker Compose (FastAPI + Neo4j + Qdrant)
- [x] `/health` endpoint
- [x] Ingestion pipeline (Phase 2): PDF parsing, chunking, extraction, confidence scoring, `POST /ingest`
- [ ] Neo4j/Qdrant indexing (Phase 3)
- [ ] Hybrid query (Phase 4)
- [ ] Synthesis + citations (Phase 5)
- [ ] Frontend (Phase 6)

## Local dev

```bash
cp .env.example .env        # fill in GROQ_API_KEY, NEO4J_PASSWORD, etc.
docker-compose up --build
```

Then check:
```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "0.1.0"}
```

Ingest a PDF:

```bash
curl -X POST http://localhost:8000/ingest \
  -F "document_id=contract_001" \
  -F "document_type=contract" \
  -F "file=@/absolute/path/to/contract.pdf"
```

The Phase 2 response reports pages, chunks, extracted entities, extracted
relationships, average confidence, and processing time. When API keys are not
available or a provider fails, ingestion uses the local deterministic fallback
so the pipeline remains runnable offline.

Neo4j browser: http://localhost:7474 (user: `neo4j`, password: whatever you set in `.env`)
Qdrant dashboard: http://localhost:6333/dashboard
