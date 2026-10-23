# DocuGraph AI

Hybrid document intelligence: vector search (Qdrant) + knowledge graph reasoning (Neo4j),
fused into auditable, citation-backed answers.

Full spec: see `DocuGraph_AI_Master_Build_Prompt.md`.

## Status: Phase 4 — Hybrid Query Processing Complete

- [x] FastAPI skeleton
- [x] Config via pydantic-settings
- [x] Docker Compose (FastAPI + Neo4j + Qdrant)
- [x] `/health` endpoint
- [x] Ingestion pipeline (Phase 2): PDF parsing, chunking, extraction, confidence scoring, `POST /ingest`
- [x] Neo4j/Qdrant indexing (Phase 3), metadata, document stats, and connectivity health
- [x] Hybrid query (Phase 4): vector search, safe graph search, query planning, and fusion
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

Check indexed document statistics:

```bash
curl http://localhost:8000/documents/contract_001/stats
```

The stats endpoint requires Neo4j and returns entity counts, average confidence
by entity type, relationship counts, and an overall extraction-quality score.

Check service connectivity:

```bash
curl http://localhost:8000/health
```

Phase 3 health reports the LLM mode plus Neo4j and Qdrant connectivity. With
Docker stopped, the API reports `degraded`; with Docker running, all three
services should report their active state.

Run a hybrid query after indexing a document:

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"Who does Alice sign with?","document_id":"contract_001","top_k":8}'
```

The response contains vector results, graph relationship results, and fused
ranked chunks. Graph retrieval uses fixed parameterized Cypher templates; user
input is never executed as Cypher.

Neo4j browser: http://localhost:7474 (user: `neo4j`, password: whatever you set in `.env`)
Qdrant dashboard: http://localhost:6333/dashboard
