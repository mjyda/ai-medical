"""kb_documents 表访问（PostgreSQL）。"""
from __future__ import annotations

from typing import Any

import psycopg2

from app.config.config import DATABASE_CONFIG
from app.database.postgresql_connection import PostgreSQLConnection

_ENSURE_SQL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS kb_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'uploaded',
    parsed_text TEXT,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_kb_documents_status ON kb_documents(status);
CREATE INDEX IF NOT EXISTS idx_kb_documents_created_at ON kb_documents(created_at DESC);
"""


class KBDocumentRepository:
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
        if KBDocumentRepository._table_ready:
            return
        try:
            with self._connect_direct() as conn:
                with conn.cursor() as cur:
                    cur.execute(_ENSURE_SQL)
                conn.commit()
            KBDocumentRepository._table_ready = True
        except Exception:
            KBDocumentRepository._table_ready = False
            raise

    def insert(self, filename: str, storage_path: str) -> str:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                raise RuntimeError("PostgreSQL 连接不可用")
            pg.execute(
                """
                INSERT INTO kb_documents (filename, storage_path, status)
                VALUES (%s, %s, 'uploaded')
                RETURNING id::text
                """,
                (filename, storage_path),
            )
            row = pg.fetch_one()
            pg.commit()
        if not row:
            raise RuntimeError("插入 kb_documents 失败")
        return row[0]

    def insert_with_id(self, doc_id: str, filename: str, storage_path: str) -> None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                raise RuntimeError("PostgreSQL 连接不可用")
            pg.execute(
                """
                INSERT INTO kb_documents (id, filename, storage_path, status)
                VALUES (%s::uuid, %s, %s, 'uploaded')
                """,
                (doc_id, filename, storage_path),
            )
            pg.commit()

    def get_by_id(self, doc_id: str) -> dict[str, Any] | None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return None
            pg.execute(
                """
                SELECT id::text, filename, storage_path, status, parsed_text, chunk_count,
                       error_message, created_at, updated_at
                FROM kb_documents WHERE id = %s::uuid
                """,
                (doc_id,),
            )
            row = pg.fetch_one()
        if not row:
            return None
        return {
            "id": row[0],
            "filename": row[1],
            "storage_path": row[2],
            "status": row[3],
            "parsed_text": row[4],
            "chunk_count": row[5],
            "error_message": row[6],
            "created_at": row[7],
            "updated_at": row[8],
        }

    def update(
        self,
        doc_id: str,
        *,
        status: str | None = None,
        parsed_text: str | None = None,
        parsed_text_null: bool = False,
        chunk_count: int | None = None,
        error_message: str | None = None,
        error_message_null: bool = False,
    ) -> bool:
        self.ensure_table()
        fields = []
        params: list[Any] = []
        if status is not None:
            fields.append("status = %s")
            params.append(status)
        if parsed_text_null:
            fields.append("parsed_text = NULL")
        elif parsed_text is not None:
            fields.append("parsed_text = %s")
            params.append(parsed_text)
        if chunk_count is not None:
            fields.append("chunk_count = %s")
            params.append(chunk_count)
        if error_message_null:
            fields.append("error_message = NULL")
        elif error_message is not None:
            fields.append("error_message = %s")
            params.append(error_message)
        if not fields:
            return True
        fields.append("updated_at = NOW()")
        params.append(doc_id)
        sql = f"UPDATE kb_documents SET {', '.join(fields)} WHERE id = %s::uuid"
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return False
            pg.execute(sql, tuple(params))
            pg.commit()
        return True

    def delete(self, doc_id: str) -> bool:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return False
            pg.execute("DELETE FROM kb_documents WHERE id = %s::uuid", (doc_id,))
            pg.commit()
        return True

    def list_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return []
            pg.execute(
                """
                SELECT id::text, filename, storage_path, status, chunk_count, error_message, created_at
                FROM kb_documents ORDER BY created_at DESC LIMIT %s
                """,
                (limit,),
            )
            rows = pg.fetch_all()
        return [
            {
                "id": r[0],
                "filename": r[1],
                "storage_path": r[2],
                "status": r[3],
                "chunk_count": r[4],
                "error_message": r[5],
                "created_at": r[6],
            }
            for r in rows
        ]
