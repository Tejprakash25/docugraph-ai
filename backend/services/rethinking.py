"""Rethink and rerank graph paths and their supporting chunks."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from services.embedding import EmbeddingService


def _hit_data(hit: Any) -> Mapping[str, Any]:
    return hit if isinstance(hit, Mapping) else vars(hit)


def _path_text(path: Sequence[Mapping[str, Any]]) -> str:
    if not path:
        return ""
    parts = [str(path[0].get("source") or "")]
    for edge in path:
        parts.extend(
            (
                str(edge.get("predicate") or ""),
                str(edge.get("target") or ""),
            )
        )
    return " ".join(part for part in parts if part).strip()


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


async def rethink_and_rank(
    query_vector: list[float],
    vector_hits: Sequence[Any],
    graph_hits: Sequence[Any],
    settings: Any,
    *,
    top_k: int = 8,
    embedder: EmbeddingService | None = None,
) -> list[dict[str, Any]]:
    """Score graph paths, then rank their provenance chunks alongside vector hits."""
    embedder = embedder or EmbeddingService()
    vector_rows = [_hit_data(hit) for hit in vector_hits]
    graph_rows = [_hit_data(hit) for hit in graph_hits]
    path_rows = [
        (hit, path, text)
        for hit in graph_rows
        if (path := hit.get("path"))
        and (text := _path_text(path))
    ]

    kept_paths: list[tuple[Mapping[str, Any], float]] = []
    if path_rows:
        # shortcut: semantic path score uses embedding similarity, not LLM path generation as in RRP; upgrade after Phase 7 benchmark.
        path_vectors = await embedder.embed_texts([text for _, _, text in path_rows])
        for (hit, path, _), path_vector in zip(path_rows, path_vectors, strict=True):
            semantic_score = max(0.0, min(_cosine(query_vector, path_vector), 1.0))
            hops = max(1, int(hit.get("hops") or len(path)))
            structural_score = math.prod(
                max(0.0, min(float(edge.get("confidence") or 0.0), 1.0))
                for edge in path
            ) / hops
            path_score = (
                settings.rethink_lambda_semantic * semantic_score
                + settings.rethink_lambda_structural * structural_score
            )
            if path_score >= settings.rethink_threshold:
                kept_paths.append((hit, path_score))

    kept_paths.sort(key=lambda item: item[1], reverse=True)
    kept_paths = kept_paths[: max(0, settings.rethink_max_paths)]

    chunks: dict[str, dict[str, Any]] = {}
    for hit in vector_rows:
        chunk_id = str(hit["chunk_id"])
        vector_score = float(hit.get("score") or 0.0)
        row = chunks.get(chunk_id)
        if row is None:
            chunks[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": hit["document_id"],
                "page_number": hit["page_number"],
                "page_numbers": hit["page_numbers"],
                "text": hit["text"],
                "vector_score": vector_score,
                "graph_score": 0.0,
                "score": vector_score,
                "path_score": 0.0,
            }
        elif vector_score > row["vector_score"]:
            row.update(
                document_id=hit["document_id"],
                page_number=hit["page_number"],
                page_numbers=hit["page_numbers"],
                text=hit["text"],
                vector_score=vector_score,
                score=vector_score,
            )

    for hit, path_score in kept_paths:
        for raw_chunk_id in hit.get("chunk_ids") or []:
            chunk_id = str(raw_chunk_id)
            row = chunks.setdefault(
                chunk_id,
                {
                    "chunk_id": chunk_id,
                    "document_id": "",
                    "page_number": 0,
                    "page_numbers": [],
                    "text": "",
                    "vector_score": 0.0,
                    "graph_score": 0.0,
                    "score": 0.0,
                    "path_score": 0.0,
                },
            )
            row["path_score"] = max(row["path_score"], path_score)
            row["graph_score"] = max(row["graph_score"], path_score)
            row["score"] = max(row["vector_score"], row["path_score"])

    ranked = sorted(chunks.values(), key=lambda row: row["score"], reverse=True)
    return [
        {
            **row,
            "vector_score": round(row["vector_score"], 4),
            "graph_score": round(row["graph_score"], 4),
            "score": round(row["score"], 4),
            "path_score": round(row["path_score"], 4),
        }
        for row in ranked[: max(1, min(top_k, 50))]
    ]
