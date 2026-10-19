"""Qdrant vector persistence for document chunks."""

from __future__ import annotations

import uuid
from typing import Any, Iterable

from config import settings


class QdrantStore:
    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        collection_name: str | None = None,
        dimension: int | None = None,
        timeout: float | None = None,
    ) -> None:
        self.url = url or settings.qdrant_url
        self.api_key = api_key or settings.qdrant_api_key or None
        self.collection_name = collection_name or settings.qdrant_collection
        self.dimension = dimension or settings.embedding_dimension
        self.timeout = timeout or settings.storage_timeout_seconds
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is None:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(url=self.url, api_key=self.api_key, timeout=self.timeout)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def health(self) -> bool:
        try:
            self._get_client().get_collections()
            return True
        except Exception:
            return False

    def ensure_collection(self) -> None:
        from qdrant_client.http import models

        client = self._get_client()
        collections = {collection.name for collection in client.get_collections().collections}
        if self.collection_name not in collections:
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.dimension, distance=models.Distance.COSINE),
            )

    def upsert_chunks(self, *, points: Iterable[dict[str, Any]]) -> None:
        from qdrant_client.http import models

        self.ensure_collection()
        qdrant_points = []
        for point in points:
            chunk_id = point["chunk_id"]
            qdrant_points.append(
                models.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id)),
                    vector=point["vector"],
                    payload=point["payload"],
                )
            )
        if qdrant_points:
            self._get_client().upsert(
                collection_name=self.collection_name,
                points=qdrant_points,
                wait=True,
            )
