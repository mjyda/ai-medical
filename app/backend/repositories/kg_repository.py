"""知识图谱 entities / relations 表访问（PostgreSQL）。"""
from __future__ import annotations

from typing import Any

import psycopg2

from app.config.config import DATABASE_CONFIG
from app.database.postgresql_connection import PostgreSQLConnection

_ENSURE_SQL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS kg_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    doc_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_kg_entities_type ON kg_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_kg_entities_doc_id ON kg_entities(doc_id);

CREATE TABLE IF NOT EXISTS kg_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id UUID NOT NULL REFERENCES kg_entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES kg_entities(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    doc_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_kg_relations_doc_id ON kg_relations(doc_id);
"""


class KGRepository:
    _table_ready = False

    def __init__(self):
        self._cfg = DATABASE_CONFIG["postgresql"]

    def _connect_direct(self):
        return psycopg2.connect(
            host=self._cfg["host"],
            port=self._cfg["port"],
            database=self._cfg["database"],
            user=self._cfg["user"],
            password=self._cfg["password"],
            connect_timeout=10,
        )

    def ensure_table(self) -> None:
        if KGRepository._table_ready:
            return
        try:
            with self._connect_direct() as conn:
                with conn.cursor() as cur:
                    cur.execute(_ENSURE_SQL)
                conn.commit()
            KGRepository._table_ready = True
        except Exception:
            KGRepository._table_ready = False
            raise

    def clear_all(self) -> None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return
            pg.execute("DELETE FROM kg_relations")
            pg.execute("DELETE FROM kg_entities")
            pg.commit()

    def insert_entity(self, name: str, entity_type: str, doc_id: str | None = None) -> str | None:
        self.ensure_table()
        existing = self.get_entity_by_name_type(name, entity_type)
        if existing:
            return existing["id"]
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return None
            pg.execute(
                """
                INSERT INTO kg_entities (name, entity_type, doc_id)
                VALUES (%s, %s, %s::uuid)
                ON CONFLICT DO NOTHING
                RETURNING id::text
                """,
                (name, entity_type, doc_id),
            )
            row = pg.fetch_one()
            pg.commit()
        return row[0] if row else None

    def insert_relation(self, source_id: str, target_id: str, relation_type: str,
                        doc_id: str | None = None) -> str | None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return None
            pg.execute(
                """
                INSERT INTO kg_relations (source_entity_id, target_entity_id, relation_type, doc_id)
                VALUES (%s::uuid, %s::uuid, %s, %s::uuid)
                RETURNING id::text
                """,
                (source_id, target_id, relation_type, doc_id),
            )
            row = pg.fetch_one()
            pg.commit()
        return row[0] if row else None

    def get_entity_by_name_type(self, name: str, entity_type: str) -> dict[str, Any] | None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return None
            pg.execute(
                """
                SELECT id::text, name, entity_type, doc_id, created_at
                FROM kg_entities WHERE name = %s AND entity_type = %s LIMIT 1
                """,
                (name, entity_type),
            )
            row = pg.fetch_one()
        if not row:
            return None
        return {"id": row[0], "name": row[1], "entity_type": row[2], "doc_id": row[3], "created_at": row[4]}

    def get_all_entities(self) -> list[dict[str, Any]]:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return []
            pg.execute(
                "SELECT id::text, name, entity_type, doc_id, created_at FROM kg_entities ORDER BY entity_type, name"
            )
            rows = pg.fetch_all()
        return [
            {"id": r[0], "name": r[1], "entity_type": r[2], "doc_id": r[3], "created_at": r[4]}
            for r in rows
        ]

    def get_all_relations(self) -> list[dict[str, Any]]:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return []
            pg.execute(
                """
                SELECT r.id::text, r.source_entity_id::text, r.target_entity_id::text,
                       r.relation_type, r.doc_id, r.created_at,
                       se.name AS source_name, se.entity_type AS source_type,
                       te.name AS target_name, te.entity_type AS target_type
                FROM kg_relations r
                JOIN kg_entities se ON r.source_entity_id = se.id
                JOIN kg_entities te ON r.target_entity_id = te.id
                ORDER BY r.created_at DESC
                """
            )
            rows = pg.fetch_all()
        return [
            {
                "id": r[0], "source_id": r[1], "target_id": r[2],
                "relation_type": r[3], "doc_id": r[4], "created_at": r[5],
                "source_name": r[6], "source_type": r[7],
                "target_name": r[8], "target_type": r[9],
            }
            for r in rows
        ]

    def get_entity_count(self) -> int:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return 0
            pg.execute("SELECT COUNT(*) FROM kg_entities")
            row = pg.fetch_one()
        return row[0] if row else 0

    def get_relation_count(self) -> int:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return 0
            pg.execute("SELECT COUNT(*) FROM kg_relations")
            row = pg.fetch_one()
        return row[0] if row else 0
