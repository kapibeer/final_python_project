# commands/manage_wardrobe.py

from dataclasses import dataclass
from typing import Optional, Any

from domain.models.clothing_item import ClothingItem
from domain.repositories.wardrobe_repository import WardrobeRepository


@dataclass
class ManageWardrobeResult:
    success: bool
    message_key: str   # "added", "updated", "deleted", "not_found"
    item: Optional[ClothingItem] = None


class ManageWardrobe:
    """
    Use-case: управление гардеробом пользователя.
    Добавление, обновление, удаление вещей.
    """

    def __init__(self, wardrobe_repo: WardrobeRepository):
        self._wardrobe_repo = wardrobe_repo

    def add_item(self, user_id: int, item: ClothingItem)\
            -> ManageWardrobeResult:
        self._wardrobe_repo.add_item(user_id, item)
        return ManageWardrobeResult(
            success=True,
            message_key="added",
            item=item
        )

    def update_item(self, user_id: int, item_id: int, **updates: Any)\
            -> ManageWardrobeResult:
        existing = self._wardrobe_repo.get_item(user_id, item_id)
        if existing is None:
            return ManageWardrobeResult(success=False, message_key="not_found")

        # обновляем только переданные поля
        for key, value in updates.items():
            if hasattr(existing, key):
                setattr(existing, key, value)

        self._wardrobe_repo.update_item(user_id, existing)
        return ManageWardrobeResult(success=True,
                                    message_key="updated",
                                    item=existing)

    def delete_item(self, user_id: int, item_id: int) -> ManageWardrobeResult:
        existing = self._wardrobe_repo.get_item(user_id, item_id)
        if existing is None:
            return ManageWardrobeResult(success=False, message_key="not_found")

        self._wardrobe_repo.delete_item(user_id, item_id)
        return ManageWardrobeResult(
            success=True,
            message_key="deleted"
            )
