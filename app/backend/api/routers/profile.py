"""个人中心路由：个人资料、修改密码、头像上传。"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.backend.api.dependencies import get_current_user
from app.backend.services.user_service import UserService
from app.config.config import AUTH_CONFIG

router = APIRouter()


class UpdateProfileBody(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=128)
    bio: str | None = None
    bio_null: bool = False
    preferences: dict | None = None


class ChangePasswordBody(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)


def _user_service() -> UserService:
    return UserService()


UserSvcDep = Depends(_user_service)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _avatar_dir() -> Path:
    return _project_root() / AUTH_CONFIG["avatar_upload_dir"]


def _safe_suffix(original: str) -> str:
    ext = Path(original).suffix.lower()
    if ext not in AUTH_CONFIG["allowed_avatar_extensions"]:
        ext = ".png"
    return ext


# ---- endpoints ----


@router.get("")
def get_profile(user: dict = Depends(get_current_user), svc: UserService = UserSvcDep):
    profile = svc.get_profile(user["id"])
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"user": profile}


@router.put("")
def update_profile(
    body: UpdateProfileBody,
    user: dict = Depends(get_current_user),
    svc: UserService = UserSvcDep,
):
    updated = svc.update_profile(
        user["id"],
        display_name=body.display_name,
        bio=body.bio,
        bio_null=body.bio_null,
        preferences=body.preferences,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"user": updated}


@router.put("/password")
def change_password(
    body: ChangePasswordBody,
    user: dict = Depends(get_current_user),
    svc: UserService = UserSvcDep,
):
    try:
        svc.change_password(user["id"], body.old_password, body.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "密码修改成功"}


@router.post("/avatar")
def upload_avatar(
    file: UploadFile,
    user: dict = Depends(get_current_user),
    svc: UserService = UserSvcDep,
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")
    ext = _safe_suffix(file.filename)
    ad = _avatar_dir()
    ad.mkdir(parents=True, exist_ok=True)
    filename = f"{user['id']}_avatar{ext}"
    dest = ad / filename
    try:
        contents = file.file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="读取文件失败")
    if len(contents) > AUTH_CONFIG["avatar_max_bytes"]:
        raise HTTPException(status_code=400, detail="头像文件不能超过 2 MB")
    dest.write_bytes(contents)
    avatar_url = f"/profile/avatar/{filename}"
    updated = svc.update_avatar(user["id"], avatar_url)
    if not updated:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"user": updated, "avatar_url": avatar_url}


@router.get("/avatar/{filename}")
def serve_avatar(filename: str):
    """直接提供头像文件（公开访问）。"""
    fp = _avatar_dir() / filename
    if not fp.exists():
        raise HTTPException(status_code=404, detail="头像不存在")
    from fastapi.responses import FileResponse

    return FileResponse(fp, media_type="image/png")
