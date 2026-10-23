from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio

from api.routes import get_indexing_service, router
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

# CORS is explicitly allowlisted; never combine wildcard origins with credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_allowed_origins.split(",")
        if origin.strip() and origin.strip() != "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(router)


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    del request
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error": str(exc.detail), "details": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    del request
    return JSONResponse(
        status_code=422,
        content={"status": "error", "error": "Invalid request", "details": str(exc.errors())},
    )


@app.get("/health")
async def health():
    storage = await asyncio.to_thread(get_indexing_service().health)
    llm_status = "connected" if settings.groq_api_key or settings.gemini_api_key else "fallback"
    services = {"llm": llm_status, **storage}
    storage_connected = all(value == "connected" for value in storage.values())
    return {
        "status": "healthy" if storage_connected else "degraded",
        "version": "0.1.0",
        "services": services,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
