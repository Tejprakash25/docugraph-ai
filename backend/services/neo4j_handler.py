"""Neo4j persistence for documents, chunks, entities, and relationships."""

from __future__ import annotations

import logging
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
        entity_rows = list(entities)
        entity_types: dict[str, set[str | None]] = {}
        for entity in entity_rows:
            entity_type = str(entity.get("type") or "").strip() or None
            entity_types.setdefault(entity["name"], set()).add(entity_type)

        with self._get_driver().session() as session:
            for entity in entity_rows:
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
            skipped_relationships = 0
            for relationship in relationships:
                # shortcut: ambiguous same-name entities are skipped; upgrade by adding types to Relationship in extraction.
                source_types = entity_types.get(relationship["source"], set())
                target_types = entity_types.get(relationship["target"], set())
                if (
                    len(source_types) != 1
                    or len(target_types) != 1
                    or None in source_types
                    or None in target_types
                ):
                    skipped_relationships += 1
                    continue
                source_type = next(iter(source_types))
                target_type = next(iter(target_types))
                session.run(
                    """
                    MATCH (source:Entity {name: $source, type: $source_type})
                    MATCH (target:Entity {name: $target, type: $target_type})
                    WHERE EXISTS {
                        MATCH (:Chunk {document_id: $document_id})-[:MENTIONS]->(source)
                    }
                    AND EXISTS {
                        MATCH (:Chunk {document_id: $document_id})-[:MENTIONS]->(target)
                    }
                    MERGE (source)-[r:RELATED {document_id: $document_id,
                                               predicate: $predicate}]->(target)
                    SET r.confidence = $confidence,
                        r.evidence = $evidence,
                        r.source_chunk_ids = $source_chunk_ids,
                        r.source_pages = $source_pages
                    """,
                    **{
                        **relationship,
                        "source_type": source_type,
                        "target_type": target_type,
                    },
                ).consume()
        if skipped_relationships:
            logging.getLogger(__name__).warning(
                "Skipped %d relationships with missing or ambiguous entity types",
                skipped_relationships,
            )

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

    def get_chunks(self, chunk_ids: list[str]) -> list[dict[str, Any]]:
        """Return persisted chunk fields for a bounded set of chunk identifiers."""
        safe_chunk_ids = list(dict.fromkeys(chunk_ids))[:50]
        if not safe_chunk_ids:
            return []
        with self._get_driver().session() as session:
            return session.run(
                """
                MATCH (c:Chunk)
                WHERE c.chunk_id IN $chunk_ids
                RETURN c.chunk_id AS chunk_id,
                       c.document_id AS document_id,
                       c.page_number AS page_number,
                       c.page_numbers AS page_numbers,
                       c.text AS text
                """,
                chunk_ids=safe_chunk_ids,
            ).data()

    def search_graph(
        self,
        *,
        entity_names: list[str],
        limit: int = 20,
        document_id: str | None = None,
        max_hops: int = 2,
    ) -> list[dict[str, Any]]:
        """Search extracted relationships using fixed, parameterized Cypher."""
        if not entity_names:
            return []
        safe_limit = max(1, min(limit, 50))
        safe_hops = max(1, min(max_hops, 3))
        query = f"""
        MATCH graph_path=(seed:Entity)-[:RELATED*1..{safe_hops}]-(target:Entity)
        WHERE any(term IN $entity_names WHERE
            toLower(seed.name) CONTAINS toLower(term) OR
            toLower(target.name) CONTAINS toLower(term))
        WITH seed, target, graph_path,
             relationships(graph_path)[0] AS rel,
             [i IN range(0, size(relationships(graph_path)) - 1) | {{
                 source: nodes(graph_path)[i].name,
                 source_type: nodes(graph_path)[i].type,
                 predicate: relationships(graph_path)[i].predicate,
                 target: nodes(graph_path)[i + 1].name,
                 target_type: nodes(graph_path)[i + 1].type,
                 confidence: relationships(graph_path)[i].confidence
             }}] AS ordered_path,
             reduce(provenance = [], path_rel IN relationships(graph_path) |
                 provenance + coalesce(path_rel.source_chunk_ids, [])) AS provenance_chunk_ids
        OPTIONAL MATCH (c:Chunk)-[:MENTIONS]->(seed)
        WHERE $document_id IS NULL OR c.document_id = $document_id
        WITH seed, target, graph_path, rel, ordered_path, provenance_chunk_ids,
             collect(DISTINCT c.chunk_id) AS mention_chunk_ids,
             collect(DISTINCT c.page_numbers)[..20] AS pages
        RETURN seed.name AS source,
               seed.type AS source_type,
               rel.predicate AS predicate,
               target.name AS target,
               target.type AS target_type,
               rel.confidence AS confidence,
               rel.evidence AS evidence,
               ordered_path AS path,
               size(relationships(graph_path)) AS hops,
               reduce(ids = [], chunk_id IN (provenance_chunk_ids + mention_chunk_ids) |
                   CASE WHEN chunk_id IS NULL OR chunk_id IN ids THEN ids
                        ELSE ids + chunk_id END)[..20] AS chunk_ids,
               pages
        ORDER BY confidence DESC
        LIMIT $limit
        """
        with self._get_driver().session() as session:
            rows = session.run(
                query,
                entity_names=entity_names,
                document_id=document_id,
                limit=safe_limit,
            ).data()
        return [
            {
                "source": row.get("source", ""),
                "source_type": row.get("source_type", "Unknown"),
                "predicate": row.get("predicate", "related_to"),
                "target": row.get("target", ""),
                "target_type": row.get("target_type", "Unknown"),
                "confidence": max(0.0, min(float(row.get("confidence") or 0.0), 1.0)),
                "evidence": row.get("evidence"),
                "chunk_ids": [str(value) for value in (row.get("chunk_ids") or []) if value],
                "pages": row.get("pages") or [],
                "score": max(0.0, min(float(row.get("confidence") or 0.0), 1.0)),
                "path": row.get("path") or [],
                "hops": int(row.get("hops") or 0),
            }
            for row in rows
        ]
