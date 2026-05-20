"""认证业务逻辑：密码哈希、JWT 签发/校验、注册/登录。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.backend.repositories.user_repository import UserRepository
from app.config.config import AUTH_CONFIG

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self._user_repo = UserRepository()

    # ---- password ----

    @staticmethod
    def hash_password(plain: str) -> str:
        return _pwd_ctx.hash(plain)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return _pwd_ctx.verify(plain, hashed)

    # ---- JWT ----

    @staticmethod
    def create_access_token(user_id: str, username: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "username": username,
            "iat": now,
            "exp": now + timedelta(minutes=AUTH_CONFIG["jwt_expire_minutes"]),
        }
        return jwt.encode(
            payload, AUTH_CONFIG["jwt_secret"], algorithm=AUTH_CONFIG["jwt_algorithm"]
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(
            token,
            AUTH_CONFIG["jwt_secret"],
            algorithms=[AUTH_CONFIG["jwt_algorithm"]],
        )

    # ---- register / login ----

    def register(self, username: str, email: str, password: str) -> dict:
        if self._user_repo.get_by_username(username):
            raise DuplicateUserError("用户名已被注册")
        if self._user_repo.get_by_email(email):
            raise DuplicateUserError("邮箱已被注册")
        hashed = self.hash_password(password)
        uid = self._user_repo.create_user(username, email, hashed)
        user = self._user_repo.get_by_id(uid)
        if not user:
            raise RuntimeError("注册后查询用户失败")
        user.pop("hashed_password", None)
        return user

    def login(self, username: str, password: str) -> dict:
        user = self._user_repo.get_by_username(username)
        if not user or not self.verify_password(password, user["hashed_password"]):
            raise InvalidCredentialsError("用户名或密码错误")
        token = self.create_access_token(user["id"], user["username"])
        user.pop("hashed_password", None)
        return {"token": token, "user": user}


class DuplicateUserError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass
