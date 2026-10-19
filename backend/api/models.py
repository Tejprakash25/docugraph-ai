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
