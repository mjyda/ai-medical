"""users 表访问（PostgreSQL）。"""
from __future__ import annotations

import json
from typing import Any

import psycopg2

from app.config.config import DATABASE_CONFIG
from app.database.postgresql_connection import PostgreSQLConnection

_ENSURE_SQL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(128),
    hashed_password TEXT NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""


class UserRepository:
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
        if UserRepository._table_ready:
            return
        try:
            with self._connect_direct() as conn:
                with conn.cursor() as cur:
                    cur.execute(_ENSURE_SQL)
                conn.commit()
            UserRepository._table_ready = True
        except Exception:
            UserRepository._table_ready = False
            raise

    # ---- helpers ----

    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        _prefs = row[7]
        if isinstance(_prefs, str):
            try:
                _prefs = json.loads(_prefs)
            except (json.JSONDecodeError, TypeError):
                _prefs = {}
        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "display_name": row[3],
            "hashed_password": row[4],
            "avatar_url": row[5],
            "bio": row[6],
            "preferences": _prefs,
            "is_active": row[8],
            "created_at": row[9],
            "updated_at": row[10],
        }

    def _row_to_public_dict(self, row: tuple) -> dict[str, Any]:
        """Same as _row_to_dict but without hashed_password."""
        d = self._row_to_dict(row)
        d.pop("hashed_password", None)
        return d

    # ---- CRUD ----

    def create_user(
        self, username: str, email: str, hashed_password: str, display_name: str | None = None
    ) -> str:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                raise RuntimeError("PostgreSQL 连接不可用")
            pg.execute(
                """
                INSERT INTO users (username, email, hashed_password, display_name)
                VALUES (%s, %s, %s, %s)
                RETURNING id::text
                """,
                (username, email, hashed_password, display_name or username),
            )
            row = pg.fetch_one()
            pg.commit()
        if not row:
            raise RuntimeError("创建用户失败")
        return row[0]

    def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return None
            pg.execute(
                """
                SELECT id::text, username, email, display_name, hashed_password,
                       avatar_url, bio, preferences, is_active, created_at, updated_at
                FROM users WHERE id = %s::uuid
                """,
                (user_id,),
            )
            row = pg.fetch_one()
        if not row:
            return None
        return self._row_to_dict(row)

    def get_by_username(self, username: str) -> dict[str, Any] | None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return None
            pg.execute(
                """
                SELECT id::text, username, email, display_name, hashed_password,
                       avatar_url, bio, preferences, is_active, created_at, updated_at
                FROM users WHERE username = %s
                """,
                (username,),
            )
            row = pg.fetch_one()
        if not row:
            return None
        return self._row_to_dict(row)

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return None
            pg.execute(
                """
                SELECT id::text, username, email, display_name, hashed_password,
                       avatar_url, bio, preferences, is_active, created_at, updated_at
                FROM users WHERE email = %s
                """,
                (email,),
            )
            row = pg.fetch_one()
        if not row:
            return None
        return self._row_to_dict(row)

    def update_profile(
        self,
        user_id: str,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        bio_null: bool = False,
        preferences: dict | None = None,
    ) -> bool:
        self.ensure_table()
        fields: list[str] = []
        params: list[Any] = []
        if display_name is not None:
            fields.append("display_name = %s")
            params.append(display_name)
        if bio_null:
            fields.append("bio = NULL")
        elif bio is not None:
            fields.append("bio = %s")
            params.append(bio)
        if preferences is not None:
            fields.append("preferences = %s::jsonb")
            params.append(json.dumps(preferences, ensure_ascii=False))
        if not fields:
            return True
        fields.append("updated_at = NOW()")
        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s::uuid"
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return False
            pg.execute(sql, tuple(params))
            pg.commit()
        return True

    def update_password(self, user_id: str, hashed_password: str) -> bool:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return False
            pg.execute(
                "UPDATE users SET hashed_password = %s, updated_at = NOW() WHERE id = %s::uuid",
                (hashed_password, user_id),
            )
            pg.commit()
        return True

    def update_avatar(self, user_id: str, avatar_url: str) -> bool:
        self.ensure_table()
        with PostgreSQLConnection() as pg:
            if not pg.cursor:
                return False
            pg.execute(
                "UPDATE users SET avatar_url = %s, updated_at = NOW() WHERE id = %s::uuid",
                (avatar_url, user_id),
            )
            pg.commit()
        return True
