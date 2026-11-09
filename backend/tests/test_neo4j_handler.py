import logging

from services.neo4j_handler import Neo4jStore


class FakeResult:
    def consume(self):
        return None

    def data(self):
        return []


class FakeSession:
    def __init__(self) -> None:
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        return FakeResult()


class FakeDriver:
    def __init__(self) -> None:
        self.fake_session = FakeSession()

    def session(self):
        return self.fake_session


def test_upsert_skips_relationship_with_ambiguous_same_name_entities(caplog) -> None:
    store = Neo4jStore()
    driver = FakeDriver()
    store._driver = driver

    with caplog.at_level(logging.WARNING):
        store.upsert_extractions(
            document_id="doc-1",
            entities=[
                {"name": "Jordan", "type": "Person", "confidence": 0.9, "chunk_id": "c1"},
                {"name": "Jordan", "type": "Organization", "confidence": 0.8, "chunk_id": "c1"},
                {"name": "Acme", "type": "Organization", "confidence": 0.9, "chunk_id": "c1"},
            ],
            relationships=[
                {
                    "document_id": "doc-1",
                    "source": "Jordan",
                    "predicate": "works_for",
                    "target": "Acme",
                    "confidence": 0.8,
                    "evidence": "Jordan works for Acme",
                    "source_chunk_ids": ["c1"],
                    "source_pages": [1],
                }
            ],
        )

    assert len(driver.fake_session.calls) == 3
    assert "Skipped 1 relationships" in caplog.text


def test_upsert_matches_entity_types_and_document_mentions() -> None:
    store = Neo4jStore()
    driver = FakeDriver()
    store._driver = driver

    store.upsert_extractions(
        document_id="doc-1",
        entities=[
            {"name": "Jordan", "type": "Person", "confidence": 0.9, "chunk_id": "c1"},
            {"name": "Acme", "type": "Organization", "confidence": 0.9, "chunk_id": "c1"},
        ],
        relationships=[
            {
                "document_id": "doc-1",
                "source": "Jordan",
                "predicate": "works_for",
                "target": "Acme",
                "confidence": 0.8,
                "evidence": "Jordan works for Acme",
                "source_chunk_ids": ["c1"],
                "source_pages": [1],
            }
        ],
    )

    query, parameters = driver.fake_session.calls[-1]
    assert "(source:Entity {name: $source, type: $source_type})" in query
    assert "(target:Entity {name: $target, type: $target_type})" in query
    assert "(:Chunk {document_id: $document_id})-[:MENTIONS]->(source)" in query
    assert "(:Chunk {document_id: $document_id})-[:MENTIONS]->(target)" in query
    assert "LIMIT 1" not in query
    assert parameters["source_type"] == "Person"
    assert parameters["target_type"] == "Organization"


def test_search_graph_caps_hops_at_three() -> None:
    store = Neo4jStore()
    driver = FakeDriver()
    store._driver = driver

    store.search_graph(entity_names=["Jordan"], max_hops=99)

    query, _ = driver.fake_session.calls[-1]
    assert "[:RELATED*1..3]" in query
