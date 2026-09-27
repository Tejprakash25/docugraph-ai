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

    # LLM APIs (used starting Phase 2 — extraction/synthesis)
    groq_api_key: str = ""
    gemini_api_key: str = ""

    # Neo4j (used starting Phase 3 — graph indexing)
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # Qdrant (used starting Phase 3 — vector indexing)
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Import this singleton everywhere instead of instantiating Settings() again
settings = Settings()
