"""FastAPI 共享依赖（认证等）。"""
from __future__ import annotations

from fastapi import Header, HTTPException

from app.backend.repositories.user_repository import UserRepository
from app.backend.services.auth_service import AuthService


def get_current_user(authorization: str = Header(...)) -> dict:
    """从 Authorization: Bearer <token> 解析并返回当前用户信息。"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = AuthService.decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌缺少用户标识")
    user = UserRepository().get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    user.pop("hashed_password", None)
    return user
