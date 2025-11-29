from typing import Protocol, Optional
from domain.models import ClothingItem


class WardrobeRepository(Protocol):
    def get(item_id: int) -> Optional[ClothingItem]:
        pass

    # если вводим id, то меняется уже существующий айтем
    def add(item: ClothingItem, item_id: Optional[int] = None) -> None:
        pass

    def delete(item_id: int) -> None:
        pass
