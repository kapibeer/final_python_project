from typing import Protocol, List, Optional, Tuple
from domain.models.weather_snap import WeatherSnap
from domain.models.user import User
from domain.models.clothing_item import ClothingItem, Style


class ItemRecommender(Protocol):
    def recommend(
            self,
            user: User,
            wardrobe: List[ClothingItem],
            weather: WeatherSnap,
            style: Optional[Style] = None) -> List[Tuple[ClothingItem, float]]:
        """Вернуть список вещей со скором"""
        ...
