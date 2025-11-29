from dataclasses import dataclass
from typing import Optional
from domain import ClothingItem, WardrobeRepository


@dataclass
class ManageWardrobeResult:
    success: bool
    message_key: str  # для рендерера: "added", "updated",
    # "deleted", "not_found"
    item: Optional[ClothingItem] = None


class ManageWardrobe:
    """
    Use-case управления гардеробом пользователя.
    """

    def __init__(self, wardrobe_repo: WardrobeRepository):
        self._wardrobe_repo = wardrobe_repo
