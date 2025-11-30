from typing import List, Optional
from domain import User, WeatherSnap, ClothingItem, Outfit, Style
from domain import OutfitRecommender


class OutfitBuilder:
    """
    Доменный сервис: собирает аутфиты, пользуясь рекомендателем.
    Рекомендатель возвращает списки вещей,
    а Builder превращает их в полноценные доменные объекты Outfit.
    """

    def __init__(self, recommender: OutfitRecommender):
        self._recommender = recommender

    def build(
        self,
        user: User,
        wardrobe: List[ClothingItem],
        weather: WeatherSnap,
        style: Optional[Style] = None,
        count_max: int = 1
    ) -> List[Outfit]:

        recommended_sets = self._recommender.recommend(
            user=user,
            wardrobe=wardrobe,
            weather=weather,
            style=style,
            count_max=count_max
        )

        outfits: List[Outfit] = [
            Outfit(items=items)
            for items in recommended_sets
        ]

        return outfits
