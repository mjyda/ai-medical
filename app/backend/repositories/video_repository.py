"""videos 表访问（PostgreSQL）。"""
from __future__ import annotations

from typing import Any

import psycopg2

from app.config.config import DATABASE_CONFIG
from app.database.postgresql_connection import PostgreSQLConnection

_ENSURE_SQL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    file_size BIGINT NOT NULL DEFAULT 0,
    mime_type VARCHAR(128),
    duration REAL,
    status VARCHAR(32) NOT NULL DEFAULT 'uploaded',
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS tags JSONB;
"""


class VideoRepository:
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
        if VideoRepository._table_ready:
            return
        try:
            with self._connect_direct() as conn:
                with conn.cursor() as cur:
                    cur.execute(_ENSURE_SQL)
                conn.commit()
            VideoRepository._table_ready = True
        except Exception:
            VideoRepository._table_ready = False
            raise

    def insert(self, filename: str, original_filename: str, storage_path: str,
               file_size: int, mime_type: str) -> str:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                raise RuntimeError("PostgreSQL 连接不可用")
            pg.execute(
                """
                INSERT INTO videos (filename, original_filename, storage_path, file_size, mime_type, status)
                VALUES (%s, %s, %s, %s, %s, 'uploaded')
                RETURNING id::text
                """,
                (filename, original_filename, storage_path, file_size, mime_type),
            )
            row = pg.fetch_one()
            pg.commit()
        if not row:
            raise RuntimeError("插入 videos 失败")
        return row[0]

    def get_by_id(self, video_id: str) -> dict[str, Any] | None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return None
            pg.execute(
                """
                SELECT id::text, filename, original_filename, storage_path, file_size,
                       mime_type, duration, status, error_message, summary, tags,
                       created_at, updated_at
                FROM videos WHERE id = %s::uuid
                """,
                (video_id,),
            )
            row = pg.fetch_one()
        if not row:
            return None
        import json
        _tags = row[10]
        if isinstance(_tags, str):
            try:
                _tags = json.loads(_tags)
            except (json.JSONDecodeError, TypeError):
                _tags = None
        return {
            "id": row[0],
            "filename": row[1],
            "original_filename": row[2],
            "storage_path": row[3],
            "file_size": row[4],
            "mime_type": row[5],
            "duration": row[6],
            "status": row[7],
            "error_message": row[8],
            "summary": row[9],
            "tags": _tags,
            "created_at": row[11],
            "updated_at": row[12],
        }

    def list_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return []
            pg.execute(
                """
                SELECT id::text, filename, original_filename, storage_path, file_size,
                       mime_type, duration, status, created_at
                FROM videos ORDER BY created_at DESC LIMIT %s
                """,
                (limit,),
            )
            rows = pg.fetch_all()
        return [
            {
                "id": r[0],
                "filename": r[1],
                "original_filename": r[2],
                "storage_path": r[3],
                "file_size": r[4],
                "mime_type": r[5],
                "duration": r[6],
                "status": r[7],
                "created_at": r[8],
            }
            for r in rows
        ]

    def update(
        self,
        video_id: str,
        *,
        status: str | None = None,
        duration: float | None = None,
        error_message: str | None = None,
        error_message_null: bool = False,
        summary: str | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        self.ensure_table()
        fields = []
        params: list[Any] = []
        if status is not None:
            fields.append("status = %s")
            params.append(status)
        if duration is not None:
            fields.append("duration = %s")
            params.append(duration)
        if error_message_null:
            fields.append("error_message = NULL")
        elif error_message is not None:
            fields.append("error_message = %s")
            params.append(error_message)
        if summary is not None:
            fields.append("summary = %s")
            params.append(summary)
        if tags is not None:
            import json
            fields.append("tags = %s::jsonb")
            params.append(json.dumps(tags, ensure_ascii=False))
        if not fields:
            return True
        fields.append("updated_at = NOW()")
        params.append(video_id)
        sql = f"UPDATE videos SET {', '.join(fields)} WHERE id = %s::uuid"
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return False
            pg.execute(sql, tuple(params))
            pg.commit()
        return True
