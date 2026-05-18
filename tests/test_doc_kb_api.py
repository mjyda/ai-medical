"""文档知识库 API 基础用例（不依赖真实 PostgreSQL 时通过依赖注入 Mock）。"""
from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.backend.api.main import app
from app.backend.api.routers import docs as docs_router
from app.config.config import KNOWLEDGE_BASE_CONFIG


class _MemRepo:
    def __init__(self):
        self.rows: dict[str, dict[str, Any]] = {}

    def ensure_table(self) -> None:
        return

    def insert_with_id(self, doc_id: str, filename: str, storage_path: str) -> None:
        self.rows[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "storage_path": storage_path,
            "status": "uploaded",
            "parsed_text": None,
            "chunk_count": 0,
            "error_message": None,
            "created_at": None,
            "updated_at": None,
        }

    def insert(self, filename: str, storage_path: str) -> str:
        import uuid

        did = str(uuid.uuid4())
        self.insert_with_id(did, filename, storage_path)
        return did

    def get_by_id(self, doc_id: str) -> dict[str, Any] | None:
        return self.rows.get(doc_id)

    def update(self, *args, **kwargs) -> bool:
        return True

    def list_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(self.rows.values())[:limit]


@pytest.fixture
def client(monkeypatch, tmp_path: Path):
    monkeypatch.setitem(KNOWLEDGE_BASE_CONFIG, "upload_dir", str(tmp_path / "kb_uploads"))
    app.dependency_overrides.clear()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_upload_rejects_oversize(client, monkeypatch):
    monkeypatch.setitem(KNOWLEDGE_BASE_CONFIG, "max_upload_bytes", 5)
    mem = _MemRepo()
    app.dependency_overrides[docs_router.get_kb_repo] = lambda: mem
    r = client.post(
        "/docs/upload",
        files=[("files", ("small.pdf", b"1234567890", "application/pdf"))],
    )
    assert r.status_code == 413


def test_upload_rejects_bad_extension(client):
    mem = _MemRepo()
    app.dependency_overrides[docs_router.get_kb_repo] = lambda: mem
    r = client.post(
        "/docs/upload",
        files=[("files", ("x.txt", b"hello", "text/plain"))],
    )
    assert r.status_code == 400


def test_batch_upload_two_files(client, tmp_path, monkeypatch):
    """规格 2.1：多文件同请求上传。"""
    monkeypatch.setitem(KNOWLEDGE_BASE_CONFIG, "upload_dir", str(tmp_path / "up_batch"))
    mem = _MemRepo()
    app.dependency_overrides[docs_router.get_kb_repo] = lambda: mem
    r = client.post(
        "/docs/upload",
        files=[
            ("files", ("a.pdf", b"%PDF-1.4 a", "application/pdf")),
            ("files", ("b.docx", b"PK\x03\x04 fake docx stub", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
        ],
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    for it in data["items"]:
        assert it["status"] == "uploaded"
        did = it["doc_id"]
        assert did in mem.rows
        assert Path(mem.rows[did]["storage_path"]).is_file()


def test_upload_ok_writes_file(client, tmp_path, monkeypatch):
    monkeypatch.setitem(KNOWLEDGE_BASE_CONFIG, "upload_dir", str(tmp_path / "up"))
    mem = _MemRepo()
    app.dependency_overrides[docs_router.get_kb_repo] = lambda: mem
    r = client.post(
        "/docs/upload",
        files=[("files", ("a.pdf", b"%PDF-1.4 minimal", "application/pdf"))],
    )
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and len(data["items"]) == 1
    did = data["items"][0]["doc_id"]
    assert did in mem.rows
    assert Path(mem.rows[did]["storage_path"]).is_file()


def test_vectorize_404(client):
    mem = _MemRepo()
    app.dependency_overrides[docs_router.get_kb_repo] = lambda: mem
    r = client.post("/docs/vectorize", json={"doc_id": "00000000-0000-0000-0000-000000000001"})
    assert r.status_code == 404


def test_vectorize_enqueues_celery_when_async(client, monkeypatch):
    """默认异步：向量化应调用 Celery task.delay，而非同步 ingest。"""
    monkeypatch.setitem(KNOWLEDGE_BASE_CONFIG, "doc_sync_ingest", False)
    queued: list[str] = []
    fake_task = MagicMock()
    fake_task.delay.side_effect = lambda doc_id: queued.append(doc_id) or {"ok": True}
    monkeypatch.setattr(docs_router, "vectorize_document_task", fake_task)
    mem = _MemRepo()
    did = "22222222-2222-2222-2222-222222222222"
    mem.insert_with_id(did, "x.pdf", str(Path("/tmp/placeholder.pdf")))
    app.dependency_overrides[docs_router.get_kb_repo] = lambda: mem
    r = client.post("/docs/vectorize", json={"doc_id": did})
    assert r.status_code == 200
    assert r.json().get("status") == "queued"
    assert queued == [did]
    fake_task.delay.assert_called_once_with(did)
