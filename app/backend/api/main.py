from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.backend.api.routers.docs import router as docs_router
from app.backend.api.routers.videos import router as videos_router
from app.backend.repositories.kb_document_repository import KBDocumentRepository
from app.backend.repositories.video_repository import VideoRepository
from app.config.config import KNOWLEDGE_BASE_CONFIG, VIDEO_CONFIG


@asynccontextmanager
async def lifespan(app: FastAPI):
    root = Path(__file__).resolve().parents[3]
    ud = root / KNOWLEDGE_BASE_CONFIG["upload_dir"]
    ud.mkdir(parents=True, exist_ok=True)
    vd = root / VIDEO_CONFIG["upload_dir"]
    vd.mkdir(parents=True, exist_ok=True)
    try:
        KBDocumentRepository().ensure_table()
    except Exception as e:
        print(f"[lifespan] kb_documents: {e}")
    try:
        VideoRepository().ensure_table()
    except Exception as e:
        print(f"[lifespan] videos: {e}")
    yield


app = FastAPI(title="Knowledge Base API", lifespan=lifespan)
app.include_router(docs_router, prefix="/docs")
app.include_router(videos_router, prefix="/videos")
