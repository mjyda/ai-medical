"""认证路由：注册、登录、获取当前用户。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.backend.api.dependencies import get_current_user
from app.backend.services.auth_service import (
    AuthService,
    DuplicateUserError,
    InvalidCredentialsError,
)

router = APIRouter()


class RegisterBody(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


class LoginBody(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


def _auth_service() -> AuthService:
    return AuthService()


AuthDep = Depends(_auth_service)


@router.post("/register", status_code=201)
def register(body: RegisterBody, auth: AuthService = AuthDep):
    try:
        user = auth.register(body.username, body.email, body.password)
    except DuplicateUserError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=409, detail=str(e))
    return {"user": user}


@router.post("/login")
def login(body: LoginBody, auth: AuthService = AuthDep):
    try:
        result = auth.login(body.username, body.password)
    except InvalidCredentialsError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail=str(e))
    return result


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"user": user}
