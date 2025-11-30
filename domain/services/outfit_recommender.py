from typing import Protocol, List, Optional
from domain import User, WeatherSnap, ClothingItem, Style


class OutfitRecommender(Protocol):
    def recommend(
        self,
        user: User,
        wardrobe: List[ClothingItem],
        weather: WeatherSnap,
        style: Optional[Style] = None,
        count_max: int = 1
    ) -> List[List[ClothingItem]]:
        """Вернуть списки вещей, которые
        должны войти в топ count_max аутфитов."""
        recommended_sets: List[List[ClothingItem]] = []
        return recommended_sets
