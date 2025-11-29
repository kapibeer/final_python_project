from typing import Protocol, Optional, List
from domain import User


class UserRepository(Protocol):
    def get(self, user_id: int) -> Optional[User]:
        """Получить пользователя по id, если он есть в системе."""
        ...

    def create(self, user: User) -> None:
        """Создать нового пользователя в хранилище."""
        ...

    def update(self, user: User) -> None:
        """Обновить данные существующего пользователя."""
        ...

    def delete(self, user_id: int) -> None:
        """Удалить пользователя (если вдруг понадобится)."""
        ...

    def get_or_create(self, user: User) -> User:
        """
        Удобный метод для онбординга:
        вернуть существующего пользователя или создать нового.
        """
        ...

    def get_all_users_with_seasonal_notifications(self) -> List[User]:
        """
        Возвращаем список всех пользователей,
        которым нужно получать сезонные уведомления.
        """
        ...
