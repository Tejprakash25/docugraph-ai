import asyncio
from types import SimpleNamespace

from services.rethinking import rethink_and_rank


class FixedEmbedder:
    def __init__(self, vectors):
        self.vectors = vectors
        self.calls = []

    async def embed_texts(self, texts):
        self.calls.append(texts)
        return self.vectors


def settings(*, threshold=0.35, max_paths=10):
    return SimpleNamespace(
        rethink_lambda_semantic=0.6,
        rethink_lambda_structural=0.4,
        rethink_threshold=threshold,
        rethink_max_paths=max_paths,
    )


def vector_hit(chunk_id, score):
    return {
        "chunk_id": chunk_id,
        "document_id": "doc-1",
        "page_number": 1,
        "page_numbers": [1],
        "text": f"Text for {chunk_id}",
        "confidence": 0.9,
        "score": score,
    }


def graph_hit(chunk_ids, *, confidence=0.9):
    path = [
        {
            "source": "Jordan",
            "source_type": "Person",
            "predicate": "works_for",
            "target": "Acme",
            "target_type": "Organization",
            "confidence": confidence,
        }
    ]
    return {
        "source": "Jordan",
        "source_type": "Person",
        "predicate": "works_for",
        "target": "Acme",
        "target_type": "Organization",
        "confidence": confidence,
        "evidence": "Jordan works for Acme",
        "chunk_ids": chunk_ids,
        "pages": [[1]],
        "score": confidence,
        "path": path,
        "hops": 1,
    }


def test_low_score_path_is_filtered_and_output_shape_is_preserved() -> None:
    embedder = FixedEmbedder([[0.0, 1.0]])

    result = asyncio.run(
        rethink_and_rank(
            [1.0, 0.0],
            [vector_hit("vector-1", 0.2)],
            [graph_hit(["graph-1"], confidence=0.1)],
            settings(),
            embedder=embedder,
        )
    )

    assert len(embedder.calls) == 1
    assert embedder.calls[0] == ["Jordan works_for Acme"]
    assert [row["chunk_id"] for row in result] == ["vector-1"]
    assert set(result[0]) == {
        "chunk_id",
        "document_id",
        "page_number",
        "page_numbers",
        "text",
        "vector_score",
        "graph_score",
        "score",
        "path_score",
    }
    assert result[0]["path_score"] == 0.0


def test_strong_path_promotes_its_chunk_over_a_weak_vector_hit() -> None:
    result = asyncio.run(
        rethink_and_rank(
            [1.0, 0.0],
            [vector_hit("weak-vector", 0.2)],
            [graph_hit(["strong-path"])],
            settings(),
            embedder=FixedEmbedder([[1.0, 0.0]]),
        )
    )

    assert [row["chunk_id"] for row in result] == ["strong-path", "weak-vector"]
    assert result[0]["score"] > result[1]["score"]
    assert result[0]["path_score"] > 0.35


def test_all_paths_filtered_falls_back_to_vector_results() -> None:
    result = asyncio.run(
        rethink_and_rank(
            [1.0, 0.0],
            [vector_hit("vector-1", 0.4)],
            [graph_hit(["filtered-path"], confidence=0.1)],
            settings(),
            embedder=FixedEmbedder([[0.0, 1.0]]),
        )
    )

    assert [row["chunk_id"] for row in result] == ["vector-1"]
    assert result[0]["score"] == 0.4
