from celery import Celery

from app.config.config import CELERY_CONFIG

celery_app = Celery(
    "kb_worker",
    broker=CELERY_CONFIG["broker_url"],
    backend=CELERY_CONFIG["result_backend"],
    include=["app.workers.tasks.doc_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
)
