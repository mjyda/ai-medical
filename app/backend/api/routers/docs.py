"""规格 3.2 文档管理 REST 接口。"""
from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.backend.repositories.kb_document_repository import KBDocumentRepository
from app.backend.services.doc_pipeline import execute_parse, execute_vectorize
from app.config.config import KNOWLEDGE_BASE_CONFIG
from app.rag.optimized_rag_service import OptimizedRAGService
from app.workers.tasks.doc_tasks import parse_document_task, vectorize_document_task

router = APIRouter()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _upload_dir() -> Path:
    return _project_root() / KNOWLEDGE_BASE_CONFIG["upload_dir"]


def _safe_filename(name: str) -> str:
    base = Path(name or "unnamed").name
    return re.sub(r"[^\w.\-()\u4e00-\u9fff]+", "_", base)[:200] or "unnamed"


class DocIdBody(BaseModel):
    doc_id: str = Field(..., min_length=1)


class SearchBody(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(5, ge=1, le=50)


def get_kb_repo() -> KBDocumentRepository:
    return KBDocumentRepository()


RepoDep = Annotated[KBDocumentRepository, Depends(get_kb_repo)]


@router.post("/upload")
async def docs_upload(
    repo: RepoDep,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(400, detail="未提供文件")
    max_b = KNOWLEDGE_BASE_CONFIG["max_upload_bytes"]
    ud = _upload_dir()
    ud.mkdir(parents=True, exist_ok=True)
    out: list[dict] = []
    for f in files:
        raw_name = f.filename or "upload.bin"
        if not (raw_name.lower().endswith(".pdf") or raw_name.lower().endswith(".docx")):
            raise HTTPException(400, detail=f"仅支持 PDF/DOCX: {raw_name}")
        safe = _safe_filename(raw_name)
        doc_id = str(uuid.uuid4())
        dest = ud / f"{doc_id}_{safe}"
        total = 0
        oversize = False
        try:
            with dest.open("wb") as wf:
                while True:
                    chunk = await f.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_b:
                        oversize = True
                        break
                    wf.write(chunk)
            if oversize:
                dest.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"文件过大（>{max_b} bytes）",
                )
        except HTTPException:
            raise
        except Exception as e:
            dest.unlink(missing_ok=True)
            raise HTTPException(500, detail=str(e)) from e
        abs_path = str(dest.resolve())
        try:
            repo.insert_with_id(doc_id, raw_name, abs_path)
        except Exception as e:
            dest.unlink(missing_ok=True)
            raise HTTPException(500, detail=str(e)) from e
        out.append({"doc_id": doc_id, "status": "uploaded"})
    return {"items": out}


@router.post("/parse")
def docs_parse(body: DocIdBody, repo: RepoDep):
    row = repo.get_by_id(body.doc_id)
    if not row:
        raise HTTPException(404, detail="文档不存在")
    if KNOWLEDGE_BASE_CONFIG["doc_sync_ingest"]:
        execute_parse(body.doc_id)
        row = repo.get_by_id(body.doc_id)
        text = (row or {}).get("parsed_text") or ""
        return {"doc_id": body.doc_id, "status": row.get("status") if row else "unknown", "parsed_text": text}
    parse_document_task.delay(body.doc_id)
    return {"doc_id": body.doc_id, "status": "queued"}


@router.post("/vectorize")
def docs_vectorize(body: DocIdBody, repo: RepoDep):
    row = repo.get_by_id(body.doc_id)
    if not row:
        raise HTTPException(404, detail="文档不存在")
    if KNOWLEDGE_BASE_CONFIG["doc_sync_ingest"]:
        execute_vectorize(body.doc_id)
        row = repo.get_by_id(body.doc_id)
        return {
            "doc_id": body.doc_id,
            "vector_id": body.doc_id,
            "status": row.get("status") if row else "unknown",
            "chunk_count": (row or {}).get("chunk_count", 0),
        }
    vectorize_document_task.delay(body.doc_id)
    return {"doc_id": body.doc_id, "vector_id": body.doc_id, "status": "queued"}


@router.post("/search")
def docs_search(body: SearchBody):
    return _do_search(body.query, body.k)


@router.get("/search")
def docs_search_get(q: str, k: int = 5):
    return _do_search(q, k)


def _do_search(query: str, k: int):
    try:
        rag = OptimizedRAGService()
        if not rag.vector_store:
            raise HTTPException(503, detail="向量库未初始化")
        pairs = rag.vector_store.similarity_search_with_relevance_scores(
            query,
            k=k,
        )
        hits = []
        for doc, score in pairs:
            hits.append(
                {
                    "doc_id": doc.metadata.get("doc_id"),
                    "snippet": (doc.page_content or "")[:400],
                    "score": float(score),
                }
            )
        return {"results": hits}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"检索失败: {e}") from e


@router.get("/")
def docs_list(repo: RepoDep, limit: int = 100):
    return {"items": repo.list_recent(min(limit, 500))}


@router.get("/{doc_id}")
def docs_detail(doc_id: str, repo: RepoDep):
    row = repo.get_by_id(doc_id)
    if not row:
        raise HTTPException(404, detail="文档不存在")
    return row
