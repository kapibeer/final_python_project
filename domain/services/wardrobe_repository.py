from typing import Protocol, Optional, List
from domain import ClothingItem


class WardrobeRepository(Protocol):
    def get_user_wardrobe(self, user_id: int) -> List[ClothingItem]:
        """Вернуть весь гардероб пользователя."""
        ...

    def get_item(self, user_id: int, item_id: int) -> Optional[ClothingItem]:
        """Вернуть одну вещь пользователя."""
        ...

    def add_item(self, user_id: int, item: ClothingItem) -> int:
        """Добавить вещь и вернуть её новый id."""
        ...

    def update_item(self, user_id: int, item: ClothingItem) -> None:
        """Обновить данные вещи пользователя."""
        ...

    def delete_item(self, user_id: int, item_id: int) -> None:
        """Удалить вещь."""
        ...
