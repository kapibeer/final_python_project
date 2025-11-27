# adapters/ml/FakeMLOutfitRecommender.py
from typing import List
from domain.models import User, WeatherSnap, ClothingItem
from domain.services import OutfitRecommender


class MLOutfitRecommender(OutfitRecommender):
    """
    Заглушка вместо ML-модели.
    """

    def recommend(
        self,
        user: User,
        weather: WeatherSnap,
        wardrobe: List[ClothingItem],
    ) -> List[ClothingItem]:
        items: List[ClothingItem] = []

        return items
