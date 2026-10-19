"""Neo4j persistence for documents, chunks, entities, and relationships."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from config import settings


class DocumentNotFoundError(LookupError):
    """Raised when no indexed document exists for a requested id."""


class Neo4jStore:
    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self.timeout = timeout or settings.storage_timeout_seconds
        self._driver: Any | None = None

    def _get_driver(self) -> Any:
        if self._driver is None:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                connection_timeout=self.timeout,
                max_connection_lifetime=300,
            )
        return self._driver

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def health(self) -> bool:
        try:
            with self._get_driver().session() as session:
                session.run("RETURN 1 AS ok").single()
            return True
        except Exception:
            return False

    def ensure_schema(self) -> None:
        statements = (
            "CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.document_id IS UNIQUE",
            "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE",
            "CREATE CONSTRAINT entity_identity_unique IF NOT EXISTS FOR (e:Entity) REQUIRE (e.type, e.name) IS UNIQUE",
            "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)",
        )
        with self._get_driver().session() as session:
            for statement in statements:
                session.run(statement).consume()

    def upsert_document(
        self,
        *,
        document_id: str,
        filename: str,
        content_hash: str,
        num_pages: int,
        document_type: str | None,
        chunks: Iterable[dict[str, Any]],
    ) -> None:
        self.ensure_schema()
        with self._get_driver().session() as session:
            session.run(
                """
                MERGE (d:Document {document_id: $document_id})
                SET d.title = $filename,
                    d.content_hash = $content_hash,
                    d.num_pages = $num_pages,
                    d.document_type = $document_type,
                    d.status = 'indexed',
                    d.ingestion_timestamp = datetime()
                """,
                document_id=document_id,
                filename=filename,
                content_hash=content_hash,
                num_pages=num_pages,
                document_type=document_type,
            ).consume()
            for chunk in chunks:
                session.run(
                    """
                    MERGE (c:Chunk {chunk_id: $chunk_id})
                    SET c.document_id = $document_id,
                        c.page_number = $page_number,
                        c.page_numbers = $page_numbers,
                        c.text = $text,
                        c.start_offset = $start_offset,
                        c.end_offset = $end_offset,
                        c.token_count = $token_count
                    WITH c
                    MATCH (d:Document {document_id: $document_id})
                    MERGE (d)-[:HAS_CHUNK]->(c)
                    """,
                    **chunk,
                ).consume()

    def upsert_extractions(
        self,
        *,
        document_id: str,
        entities: Iterable[dict[str, Any]],
        relationships: Iterable[dict[str, Any]],
    ) -> None:
        with self._get_driver().session() as session:
            for entity in entities:
                session.run(
                    """
                    MERGE (e:Entity {type: $type, name: $name})
                    SET e.confidence = CASE
                        WHEN coalesce(e.confidence, 0.0) < $confidence THEN $confidence
                        ELSE e.confidence END
                    WITH e
                    MATCH (c:Chunk {chunk_id: $chunk_id})
                    MERGE (c)-[:MENTIONS]->(e)
                    """,
                    **entity,
                ).consume()
            for relationship in relationships:
                session.run(
                    """
                    MATCH (source:Entity {name: $source})
                    MATCH (target:Entity {name: $target})
                    WITH source, target LIMIT 1
                    MERGE (source)-[r:RELATED {document_id: $document_id,
                                               predicate: $predicate}]->(target)
                    SET r.confidence = $confidence,
                        r.evidence = $evidence,
                        r.source_chunk_ids = $source_chunk_ids,
                        r.source_pages = $source_pages
                    """,
                    **relationship,
                ).consume()

    def get_document_stats(self, document_id: str) -> dict[str, Any]:
        with self._get_driver().session() as session:
            exists = session.run(
                "MATCH (d:Document {document_id: $document_id}) RETURN d.document_id AS document_id, d.status AS status",
                document_id=document_id,
            ).single()
            if exists is None:
                raise DocumentNotFoundError(document_id)

            entity_rows = session.run(
                """
                MATCH (d:Document {document_id: $document_id})-[:HAS_CHUNK]->(:Chunk)-[:MENTIONS]->(e:Entity)
                RETURN e.type AS type, count(e) AS count, avg(e.confidence) AS confidence
                """,
                document_id=document_id,
            ).data()
            relationship_rows = session.run(
                """
                MATCH (:Entity)-[r:RELATED {document_id: $document_id}]->(:Entity)
                RETURN r.predicate AS predicate, count(r) AS count
                """,
                document_id=document_id,
            ).data()

        entities_by_type = {row["type"]: row["count"] for row in entity_rows}
        avg_confidence_by_type = {
            row["type"]: round(float(row["confidence"] or 0.0), 4) for row in entity_rows
        }
        relationships_by_predicate = {row["predicate"]: row["count"] for row in relationship_rows}
        confidence_values = list(avg_confidence_by_type.values())
        overall = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
        return {
            "document_id": document_id,
            "status": exists["status"] or "indexed",
            "extraction_quality": {
                "entities_by_type": entities_by_type,
                "avg_confidence_by_type": avg_confidence_by_type,
                "relationships_by_predicate": relationships_by_predicate,
                "overall_quality_score": round(overall, 4),
            },
        }
