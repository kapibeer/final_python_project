from dataclasses import dataclass
from typing import Optional
from domain import User, UserRepository


@dataclass
class ManageUserPreferencesResult:
    success: bool
    message_key: str  # "updated", "not_found" и тд
    user: Optional[User] = None


class ManageUserPreferences:
    """
    Use-case изменения пользовательских настроек.
    Работает только с доменными моделями и репозиторием.
    """

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo
