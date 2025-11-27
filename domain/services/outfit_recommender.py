from typing import Protocol, List
from domain.models import User, WeatherSnap, ClothingItem


class OutfitRecommender(Protocol):
    def recommend(
        self,
        user: User,
        weather: WeatherSnap,
        wardrobe: List[ClothingItem],
    ) -> List[ClothingItem]:
        """Вернуть список вещей, которые должны войти в аутфит."""
        return []
