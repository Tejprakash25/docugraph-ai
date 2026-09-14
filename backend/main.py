from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import router
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting DocuGraph AI...")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="DocuGraph AI",
    description="Hybrid Knowledge Graph RAG for Document Intelligence",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — tighten allow_origins to the Vercel frontend URL before deploying
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    """
    Phase 1 version: just confirms the API process is up.
    Phase 3 will extend this to report Neo4j/Qdrant connectivity
    (see TRD Endpoint 4 spec).
    """
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
