from dataclasses import dataclass
from typing import Optional, Any
from domain.models.user import User
from domain.repositories.user_repository import UserRepository


@dataclass
class ManageUserPreferencesResult:
    success: bool
    message_key: str      # "updated", "not_found"
    user: Optional[User] = None


class ManageUserPreferences:
    """
    Use-case: управление пользователем.
    Обновляет отдельные поля в доменной модели пользователя.
    """

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def update_preferences(self, user_id: int, **updates: Any)\
            -> ManageUserPreferencesResult:
        """
        Обновляет только те поля, которые пришли в updates.
        Например: update_preferences(id, age=20, style="casual")
        """
        user = self._user_repo.get(user_id)
        if user is None:
            return ManageUserPreferencesResult(
                success=False,
                message_key="not_found"
            )

        # применяем каждое переданное обновление
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self._user_repo.update(user)

        return ManageUserPreferencesResult(
            success=True,
            message_key="updated",
            user=user
        )
