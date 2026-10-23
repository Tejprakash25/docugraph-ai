"""Pydantic models for the public API and ingestion data contracts."""

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    status: str = "success"
    document_id: str
    chunks_created: int = Field(ge=0)
    entities_extracted: int = Field(ge=0)
    relationships_extracted: int = Field(ge=0)
    avg_confidence: float = Field(ge=0, le=1)
    pages: int = Field(ge=0)
    processing_time_seconds: float = Field(ge=0)


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    details: str | None = None


class ExtractionQuality(BaseModel):
    entities_by_type: dict[str, int]
    avg_confidence_by_type: dict[str, float]
    relationships_by_predicate: dict[str, int]
    overall_quality_score: float = Field(ge=0, le=1)


class DocumentStatsResponse(BaseModel):
    document_id: str
    status: str
    extraction_quality: ExtractionQuality


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    document_id: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
    top_k: int = Field(default=8, ge=1, le=50)
    graph_limit: int = Field(default=20, ge=1, le=50)
    max_hops: int = Field(default=2, ge=1, le=2)


class QueryResponse(BaseModel):
    status: str = "success"
    query: str
    vector_results: list[dict]
    graph_results: list[dict]
    fused_results: list[dict]
    query_plan: dict
