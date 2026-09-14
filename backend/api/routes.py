"""
API routes live here.

Phase 1: just the router shell — /health is defined directly on the app
in main.py since it has no dependencies on services that don't exist yet.

Phase 2 adds: POST /ingest
Phase 4 adds: POST /query
Phase 3 adds: GET /documents/{document_id}/stats
"""
from fastapi import APIRouter

router = APIRouter()

# Routes get added here in later phases, e.g.:
# @router.post("/ingest")
# async def ingest_document(...): ...
