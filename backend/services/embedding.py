"""Embedding generation for Qdrant chunk indexing."""

from __future__ import annotations

import asyncio
import hashlib
import math
from typing import Any

from config import settings


class EmbeddingService:
    """Use MiniLM when available and a stable 384D fallback when it is not."""

    def __init__(
        self,
        model_name: str | None = None,
        dimension: int | None = None,
        allow_fallback: bool | None = None,
        force_fallback: bool = False,
    ) -> None:
        self.model_name = model_name or settings.embedding_model
        self.dimension = dimension or settings.embedding_dimension
        self.allow_fallback = settings.embedding_allow_fallback if allow_fallback is None else allow_fallback
        self.force_fallback = force_fallback
        self._model: Any | None = None
        self._model_load_attempted = False

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await asyncio.to_thread(self._embed_sync, texts)

    def _embed_sync(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        if model is not None:
            vectors = model.encode(texts, normalize_embeddings=True)
            return [self._fit_dimension([float(value) for value in vector], self.dimension) for vector in vectors]
        if not self.allow_fallback:
            raise RuntimeError("Sentence-transformers model is unavailable and fallback is disabled")
        return [self._fallback_embedding(text) for text in texts]

    def _load_model(self) -> Any | None:
        if self.force_fallback or self._model_load_attempted:
            return self._model
        self._model_load_attempted = True
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        except Exception:
            self._model = None
        return self._model

    def _fallback_embedding(self, text: str) -> list[float]:
        values: list[float] = []
        seed = text.encode("utf-8")
        counter = 0
        while len(values) < self.dimension:
            digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
            values.extend((byte / 127.5) - 1.0 for byte in digest)
            counter += 1
        return self._fit_dimension(values[: self.dimension], self.dimension)

    @staticmethod
    def _fit_dimension(values: list[float], dimension: int) -> list[float]:
        target = dimension
        fitted = (values + [0.0] * target)[:target]
        norm = math.sqrt(sum(value * value for value in fitted))
        if norm == 0:
            return [0.0] * target
        return [round(value / norm, 8) for value in fitted]
