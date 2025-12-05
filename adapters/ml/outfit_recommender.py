from typing import List
from domain import User, WeatherSnap
from domain import ClothingItem, OutfitRecommender


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
