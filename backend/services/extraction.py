"""Confidence-scored entity and relationship extraction for document chunks."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Entity:
    name: str
    type: str
    confidence: float
    context: str | None = None


@dataclass(frozen=True)
class Relationship:
    source: str
    predicate: str
    target: str
    confidence: float
    evidence: str | None = None


@dataclass
class ExtractionResult:
    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    provider: str = "unknown"

    @property
    def confidence_values(self) -> list[float]:
        return [entity.confidence for entity in self.entities] + [
            relationship.confidence for relationship in self.relationships
        ]


class ExtractionProvider(Protocol):
    async def extract(self, text: str) -> ExtractionResult:
        ...


def _confidence(value: Any, default: float = 0.5) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(0.0, min(1.0, parsed))


def _clean_name(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip(" \t\n.,;:")


def parse_extraction_payload(payload: str | dict[str, Any]) -> ExtractionResult:
    """Parse and sanitize provider JSON so malformed model output cannot leak through."""
    if isinstance(payload, str):
        content = payload.strip()
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.IGNORECASE)
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid extraction JSON") from exc

    if not isinstance(payload, dict):
        raise ValueError("LLM extraction payload must be a JSON object")

    entities: list[Entity] = []
    seen_entities: set[tuple[str, str]] = set()
    for raw in payload.get("entities", []):
        if not isinstance(raw, dict):
            continue
        name = _clean_name(raw.get("name"))
        entity_type = _clean_name(raw.get("type") or "Unknown") or "Unknown"
        if not name:
            continue
        key = (name.casefold(), entity_type.casefold())
        if key in seen_entities:
            continue
        seen_entities.add(key)
        entities.append(
            Entity(
                name=name,
                type=entity_type,
                confidence=_confidence(raw.get("confidence")),
                context=_clean_name(raw.get("context")) or None,
            )
        )

    relationships: list[Relationship] = []
    seen_relationships: set[tuple[str, str, str]] = set()
    for raw in payload.get("relationships", []):
        if not isinstance(raw, dict):
            continue
        source = _clean_name(raw.get("source"))
        predicate = _clean_name(raw.get("predicate") or raw.get("relationship"))
        target = _clean_name(raw.get("target"))
        if not source or not predicate or not target:
            continue
        key = (source.casefold(), predicate.casefold(), target.casefold())
        if key in seen_relationships:
            continue
        seen_relationships.add(key)
        relationships.append(
            Relationship(
                source=source,
                predicate=predicate,
                target=target,
                confidence=_confidence(raw.get("confidence")),
                evidence=_clean_name(raw.get("evidence")) or None,
            )
        )

    return ExtractionResult(entities=entities, relationships=relationships)


class HeuristicExtractor:
    """Offline fallback used when provider keys are absent or APIs fail."""

    _date_pattern = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
    _amount_pattern = re.compile(
        r"(?<!\w)(?:[$€£]\s?\d[\d,]*(?:\.\d{1,2})?|\d[\d,]*(?:\.\d{1,2})?\s+(?:dollars?|euros?|pounds?))\b",
        re.I,
    )
    _org_pattern = re.compile(
        r"\b[A-Z][\w&.-]*(?:\s+[A-Z][\w&.-]*){0,3}\s+(?:Inc\.?|Corp\.?|Corporation|Ltd\.?|LLC|Company|Co\.?)\b"
    )
    _person_pattern = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b")
    _relation_pattern = re.compile(
        r"(?P<source>[A-Z][\w&.-]*(?:\s+[A-Z][\w&.-]*){0,3})\s+"
        r"(?P<predicate>signs?|pays?|owns?|works?\s+for|reports?\s+to|supplies?)\s+"
        r"(?P<target>[A-Z][\w&.-]*(?:\s+[A-Z][\w&.-]*){0,3})",
        re.IGNORECASE,
    )

    async def extract(self, text: str) -> ExtractionResult:
        entities: list[Entity] = []
        occupied: set[tuple[int, int]] = set()

        def add_matches(pattern: re.Pattern[str], entity_type: str, confidence: float) -> None:
            for match in pattern.finditer(text):
                name = _clean_name(match.group(0))
                span = match.span()
                if not name or any(
                    start <= span[0] < end or start < span[1] <= end
                    for start, end in occupied
                ):
                    continue
                occupied.add(span)
                entities.append(Entity(name, entity_type, confidence, match.group(0)))

        add_matches(self._org_pattern, "Organization", 0.9)
        add_matches(self._amount_pattern, "Amount", 0.92)
        add_matches(self._date_pattern, "Date", 0.95)
        add_matches(self._person_pattern, "Person", 0.7)

        relationships: list[Relationship] = []
        for match in self._relation_pattern.finditer(text):
            source = _clean_name(match.group("source"))
            target = _clean_name(match.group("target"))
            predicate = re.sub(r"\s+", "_", match.group("predicate").lower())
            relationships.append(
                Relationship(
                    source=source,
                    predicate=predicate,
                    target=target,
                    confidence=0.65,
                    evidence=match.group(0),
                )
            )
        return ExtractionResult(entities=entities, relationships=relationships, provider="heuristic")


EXTRACTION_PROMPT = """You extract factual entities and relationships from one document chunk.
Return JSON only with this exact shape:
{"entities":[{"name":"...","type":"Person|Organization|Date|Amount|Other","confidence":0.0,"context":"..."}],
 "relationships":[{"source":"...","predicate":"...","target":"...","confidence":0.0,"evidence":"..."}]}
Use only facts explicitly present in the chunk. Confidence must be between 0 and 1.
Do not infer facts, do not invent entities, and do not include a relationship unless both endpoints are explicit.

CHUNK:
"""


class GroqProvider:
    def __init__(self, api_key: str, model: str, timeout: float = 30.0) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def extract(self, text: str) -> ExtractionResult:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=self.api_key, timeout=self.timeout)
        response = await client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT.split("CHUNK:")[0]},
                {"role": "user", "content": f"{EXTRACTION_PROMPT}\n{text}"},
            ],
        )
        result = parse_extraction_payload(response.choices[0].message.content or "{}")
        result.provider = "groq"
        return result


class GeminiProvider:
    def __init__(self, api_key: str, model: str, timeout: float = 30.0) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def extract(self, text: str) -> ExtractionResult:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        response = await client.aio.models.generate_content(
            model=self.model,
            contents=f"{EXTRACTION_PROMPT}\n{text}",
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )
        result = parse_extraction_payload(response.text or "{}")
        result.provider = "gemini"
        return result


class ResilientExtractor:
    """Groq -> Gemini -> deterministic local fallback."""

    def __init__(
        self,
        groq_api_key: str = "",
        gemini_api_key: str = "",
        groq_model: str = "llama-3.1-8b-instant",
        gemini_model: str = "gemini-2.0-flash",
        timeout: float = 30.0,
    ) -> None:
        self.providers: list[ExtractionProvider] = []
        if groq_api_key:
            self.providers.append(GroqProvider(groq_api_key, groq_model, timeout))
        if gemini_api_key:
            self.providers.append(GeminiProvider(gemini_api_key, gemini_model, timeout))
        self.fallback = HeuristicExtractor()

    async def extract(self, text: str) -> ExtractionResult:
        for provider in self.providers:
            try:
                return await provider.extract(text)
            except Exception:
                continue
        return await self.fallback.extract(text)
