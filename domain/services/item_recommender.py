from typing import Protocol, List, Optional, Tuple
from domain import User, WeatherSnap, ClothingItem, Style


class ItemRecommender(Protocol):
    def recommend(
            self,
            user: User,
            wardrobe: List[ClothingItem],
            weather: WeatherSnap,
            style: Optional[Style] = None) -> List[Tuple[ClothingItem, float]]:
        """Вернуть список вещей со скором"""
        ...
