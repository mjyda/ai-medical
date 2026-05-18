"""视频管理 REST 接口。"""
from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

import yt_dlp
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.backend.repositories.video_repository import VideoRepository
from app.config.config import VIDEO_CONFIG

router = APIRouter()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _upload_dir() -> Path:
    return _project_root() / VIDEO_CONFIG["upload_dir"]


def _safe_filename(name: str) -> str:
    base = Path(name or "unnamed").name
    return re.sub(r"[^\w.\-()一-鿿]+", "_", base)[:200] or "unnamed"


def get_video_repo() -> VideoRepository:
    return VideoRepository()


RepoDep = Depends(get_video_repo)


class DownloadBody(BaseModel):
    url: str = Field(..., min_length=1)
    max_height: int = Field(1080, ge=360, le=2160)


def _find_ffmpeg() -> str | None:
    """查找 ffmpeg 二进制路径（优先 imageio-ffmpeg 内置）。"""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    import shutil
    found = shutil.which("ffmpeg")
    return found


def _run_download(url: str, max_height: int, output_dir: Path, video_id: str, cookies_file: str) -> dict:
    """使用 yt-dlp 下载视频，返回信息 dict。"""
    output_template = str(output_dir / f"{video_id}_%(title).200s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "format": f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,
    }
    ffmpeg_path = _find_ffmpeg()
    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path
    if cookies_file and Path(cookies_file).is_file():
        ydl_opts["cookiefile"] = cookies_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # 查找下载的文件
    actual_file = None
    for f in output_dir.iterdir():
        if f.name.startswith(video_id) and f.suffix.lower() in VIDEO_CONFIG["allowed_extensions"]:
            actual_file = f
            # 优先选 mp4
            if f.suffix.lower() == ".mp4":
                break

    if not actual_file:
        raise RuntimeError("下载完成但未找到输出文件")

    return {
        "title": info.get("title", "untitled"),
        "duration": info.get("duration"),
        "file_size": actual_file.stat().st_size,
        "storage_path": str(actual_file.resolve()),
        "filename": actual_file.name,
    }


@router.post("/upload")
async def video_upload(
    repo: VideoRepository = RepoDep,
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(400, detail="未提供文件")
    raw_name = file.filename
    ext = Path(raw_name).suffix.lower()
    allowed = VIDEO_CONFIG["allowed_extensions"]
    if ext not in allowed:
        raise HTTPException(400, detail=f"不支持的格式 {ext}，允许: {allowed}")
    max_b = VIDEO_CONFIG["max_upload_bytes"]
    ud = _upload_dir()
    ud.mkdir(parents=True, exist_ok=True)
    safe = _safe_filename(raw_name)
    video_id = str(uuid.uuid4())
    dest_filename = f"{video_id}_{safe}"
    dest = ud / dest_filename
    total = 0
    try:
        with dest.open("wb") as wf:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_b:
                    dest.unlink(missing_ok=True)
                    raise HTTPException(413, detail=f"文件过大（>{max_b} bytes）")
                wf.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(500, detail=str(e)) from e
    abs_path = str(dest.resolve())
    mime_type = file.content_type or "application/octet-stream"
    try:
        repo.insert(dest_filename, raw_name, abs_path, total, mime_type)
    except Exception as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(500, detail=str(e)) from e
    return {
        "video_id": video_id,
        "filename": raw_name,
        "file_size": total,
        "status": "uploaded",
    }


@router.post("/download")
def video_download(body: DownloadBody, repo: VideoRepository = RepoDep):
    url = body.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(400, detail="请提供有效的 http/https 链接")
    max_height = body.max_height
    ud = _upload_dir()
    ud.mkdir(parents=True, exist_ok=True)
    video_id = str(uuid.uuid4())
    cookies_file = VIDEO_CONFIG.get("download_cookies_file", "")
    try:
        info = _run_download(url, max_height, ud, video_id, cookies_file)
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(400, detail=f"下载失败: {e}") from e
    except Exception as e:
        raise HTTPException(500, detail=str(e)) from e

    try:
        repo.insert(info["filename"], info["title"], info["storage_path"],
                    info["file_size"], "video/mp4")
    except Exception as e:
        Path(info["storage_path"]).unlink(missing_ok=True)
        raise HTTPException(500, detail=str(e)) from e
    return {
        "video_id": video_id,
        "filename": info["title"],
        "file_size": info["file_size"],
        "duration": info["duration"],
        "status": "uploaded",
    }


@router.post("/{video_id}/analyze")
def video_analyze(video_id: str, repo: VideoRepository = RepoDep):
    row = repo.get_by_id(video_id)
    if not row:
        raise HTTPException(404, detail="视频不存在")
    title = row.get("original_filename") or row.get("filename") or ""
    if not title.strip():
        raise HTTPException(400, detail="视频缺少标题信息，无法分析")

    from app.backend.services.video_analysis_service import VideoAnalysisService

    try:
        service = VideoAnalysisService()
        summary, tags, related_docs = service.run_full_analysis(title)
    except Exception as e:
        raise HTTPException(500, detail=f"分析失败: {e}") from e

    repo.update(video_id, summary=summary, tags=tags)

    return {
        "video_id": video_id,
        "summary": summary,
        "tags": tags,
        "related_documents": related_docs,
    }


@router.get("/")
def video_list(limit: int = 100, repo: VideoRepository = RepoDep):
    return {"items": repo.list_recent(min(limit, 500))}


@router.get("/{video_id}")
def video_detail(video_id: str, repo: VideoRepository = RepoDep):
    row = repo.get_by_id(video_id)
    if not row:
        raise HTTPException(404, detail="视频不存在")
    return row


@router.get("/{video_id}/file")
def video_file(video_id: str, repo: VideoRepository = RepoDep):
    row = repo.get_by_id(video_id)
    if not row:
        raise HTTPException(404, detail="视频不存在")
    path = row["storage_path"]
    if not Path(path).is_file():
        raise HTTPException(404, detail="视频文件不存在")
    return FileResponse(
        path,
        media_type=row.get("mime_type") or "application/octet-stream",
        filename=row.get("original_filename") or row.get("filename"),
    )
