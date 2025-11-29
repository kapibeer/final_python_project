from typing import Protocol, Optional
from domain.models import User


class UserRepository(Protocol):
    def get(user_id: int) -> Optional[User]:
        pass

    # если вводим id, то меняется уже существующий юсер
    def add(user: User, user_id: Optional[int] = None) -> None:
        pass

    def delete(user_id: int) -> None:
        pass
