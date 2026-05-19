"""文档解析/向量化同步逻辑（供 Celery 与 API 同步模式复用）。"""
from __future__ import annotations

import traceback

from app.backend.repositories.kb_document_repository import KBDocumentRepository
from app.rag.document_ingest import joined_preview_text, load_documents_from_file
from app.rag.optimized_rag_service import OptimizedRAGService


def execute_parse(doc_id: str) -> dict:
    repo = KBDocumentRepository()
    row = repo.get_by_id(doc_id)
    if not row:
        return {"ok": False, "error": "not_found"}
    path = row["storage_path"]
    try:
        repo.update(doc_id, status="parsing", error_message_null=True)
        docs = load_documents_from_file(path, doc_id)
        if not docs:
            repo.update(
                doc_id,
                status="failed",
                error_message="无法解析该文件格式或文件为空",
            )
            return {"ok": False, "doc_id": doc_id}
        preview = joined_preview_text(docs)
        repo.update(
            doc_id,
            status="parsed",
            parsed_text=preview,
            error_message_null=True,
        )
        return {"ok": True, "doc_id": doc_id, "chars": len(preview)}
    except Exception as e:
        err = f"{e}\n{traceback.format_exc()}"
        repo.update(doc_id, status="failed", error_message=err[:8000])
        return {"ok": False, "doc_id": doc_id, "error": str(e)}


def execute_vectorize(doc_id: str) -> dict:
    repo = KBDocumentRepository()
    row = repo.get_by_id(doc_id)
    if not row:
        return {"ok": False, "error": "not_found"}
    path = row["storage_path"]
    if row["status"] == "vectorized":
        return {"ok": True, "doc_id": doc_id, "chunks": row["chunk_count"], "skipped": True}
    if row["status"] not in ("parsed", "uploaded"):
        repo.update(
            doc_id,
            status="failed",
            error_message=f"向量化前状态非法: {row['status']}",
        )
        return {"ok": False, "doc_id": doc_id}
    try:
        repo.update(doc_id, status="vectorizing", error_message_null=True)
        rag = OptimizedRAGService()
        n = rag.ingest_file_for_doc(doc_id, path)
        repo.update(
            doc_id,
            status="vectorized",
            chunk_count=n,
            error_message_null=True,
        )
        return {"ok": True, "doc_id": doc_id, "chunks": n}
    except Exception as e:
        err = f"{e}\n{traceback.format_exc()}"
        repo.update(doc_id, status="failed", error_message=err[:8000])
        return {"ok": False, "doc_id": doc_id, "error": str(e)}
