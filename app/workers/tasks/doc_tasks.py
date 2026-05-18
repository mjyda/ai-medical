"""文档解析与向量化 Celery 任务。"""
from __future__ import annotations

from app.backend.services.doc_pipeline import execute_parse, execute_vectorize
from app.workers.celery_app import celery_app


@celery_app.task
def parse_document_task(doc_id: str) -> dict:
    return execute_parse(doc_id)


@celery_app.task
def vectorize_document_task(doc_id: str) -> dict:
    return execute_vectorize(doc_id)
