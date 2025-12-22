from typing import Protocol, Optional, List
from domain.models.clothing_item import ClothingItem


class WardrobeRepository(Protocol):
    async def get_user_wardrobe(self, user_id: int) -> List[ClothingItem]:
        """Вернуть весь гардероб пользователя."""
        ...

    async def get_item(self, user_id: int, item_id: int) \
            -> Optional[ClothingItem]:
        """Вернуть одну вещь пользователя."""
        ...

    async def add_item(self, user_id: int, item: ClothingItem) -> int:
        """Добавить вещь и вернуть её новый id."""
        ...

    async def update_item(self, user_id: int, item: ClothingItem) -> None:
        """Обновить данные вещи пользователя."""
        ...

    async def delete_item(self, user_id: int, item_id: int) -> None:
        """Удалить вещь."""
        ...
