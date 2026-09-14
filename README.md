# DocuGraph AI

Hybrid document intelligence: vector search (Qdrant) + knowledge graph reasoning (Neo4j),
fused into auditable, citation-backed answers.

Full spec: see `DocuGraph_AI_Master_Build_Prompt.md`.

## Status: Phase 1 — Foundational Setup

- [x] FastAPI skeleton
- [x] Config via pydantic-settings
- [x] Docker Compose (FastAPI + Neo4j + Qdrant)
- [x] `/health` endpoint
- [ ] Ingestion pipeline (Phase 2)
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

Neo4j browser: http://localhost:7474 (user: `neo4j`, password: whatever you set in `.env`)
Qdrant dashboard: http://localhost:6333/dashboard
