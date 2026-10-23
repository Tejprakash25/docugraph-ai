"""
Centralized app settings. Everything pulls from environment variables
(populated from .env locally, or container env vars in Railway).

Add new config values here as later phases need them — don't scatter
os.getenv() calls through the codebase.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    fastapi_env: str = "development"
    debug: bool = True
    cors_allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # LLM APIs (used starting Phase 2 — extraction/synthesis)
    groq_api_key: str = ""
    gemini_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    gemini_model: str = "gemini-2.0-flash"
    llm_timeout_seconds: float = 30.0
    extraction_concurrency: int = 4
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_allow_fallback: bool = True

    # Neo4j (used starting Phase 3 — graph indexing)
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # Qdrant (used starting Phase 3 — vector indexing)
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "docugraph_chunks"
    storage_timeout_seconds: float = 2.0

    # Ingestion (Phase 2)
    max_upload_size_mb: int = 50
    chunk_size_tokens: int = 400
    chunk_overlap_tokens: int = 50

    # The shared project .env also contains variables owned by later phases
    # (for example, the frontend API URL). Ignore those unrelated keys while
    # still validating every backend setting declared above.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Import this singleton everywhere instead of instantiating Settings() again
settings = Settings()
