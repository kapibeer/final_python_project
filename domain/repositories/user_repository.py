from typing import Protocol, Optional, List
from domain.models.user import User
from datetime import time


class UserRepository(Protocol):
    async def get(self, user_id: int) -> Optional[User]:
        """Получить пользователя по id, если он есть в системе."""
        ...

    async def create(self, user: User) -> None:
        """Создать нового пользователя в хранилище."""
        ...

    async def update(self, user: User) -> None:
        """Обновить данные существующего пользователя."""
        ...

    async def delete(self, user_id: int) -> None:
        """Удалить пользователя (если вдруг понадобится)."""
        ...

    async def get_or_create(self, user: User) -> User:
        """
        Удобный метод для онбординга:
        вернуть существующего пользователя или создать нового.
        """
        ...

    async def get_all_users_with_seasonal_notifications(self) -> List[User]:
        """
        Возвращаем список всех пользователей,
        которым нужно получать сезонные уведомления.
        """
        ...

    async def get_users_to_notify_between(self, start: time, end: time) \
            -> List[User]:
        """Пользователи, чьё
        notification_time попадает в [start, end]."""
        ...
