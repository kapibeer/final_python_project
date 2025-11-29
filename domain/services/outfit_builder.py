# domain/services/OutfitBuilder.py
from typing import List
from domain import User, WeatherSnap, ClothingItem, Outfit
from domain import OutfitRecommender


class OutfitBuilder:
    """
    Доменный сервис: собирает аутфит, пользуясь абстрактным рекомендателем.
    Сейчас в проект будет подставлена заглушка, позже — настоящая ML-модель.
    """

    def __init__(self, recommender: OutfitRecommender):
        self._recommender = recommender

    def build(
        self,
        user: User,
        weather: WeatherSnap,
        wardrobe: List[ClothingItem],
    ) -> Outfit:
        items = self._recommender.recommend(user, weather, wardrobe)
        return Outfit(
            items=items
        )
