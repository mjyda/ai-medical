"""用户业务逻辑：个人资料、修改密码、头像。"""
from __future__ import annotations

from app.backend.repositories.user_repository import UserRepository
from app.backend.services.auth_service import AuthService


class UserService:
    def __init__(self):
        self._user_repo = UserRepository()
        self._auth = AuthService()

    def get_profile(self, user_id: str) -> dict | None:
        user = self._user_repo.get_by_id(user_id)
        if user:
            user.pop("hashed_password", None)
        return user

    def update_profile(
        self,
        user_id: str,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        bio_null: bool = False,
        preferences: dict | None = None,
    ) -> dict | None:
        self._user_repo.update_profile(
            user_id,
            display_name=display_name,
            bio=bio,
            bio_null=bio_null,
            preferences=preferences,
        )
        return self.get_profile(user_id)

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> None:
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        if not self._auth.verify_password(old_password, user["hashed_password"]):
            raise ValueError("当前密码错误")
        hashed = self._auth.hash_password(new_password)
        self._user_repo.update_password(user_id, hashed)

    def update_avatar(self, user_id: str, avatar_url: str) -> dict | None:
        self._user_repo.update_avatar(user_id, avatar_url)
        return self.get_profile(user_id)
