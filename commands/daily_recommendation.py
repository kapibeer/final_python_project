from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from domain import (
    Outfit, TakeWith,
    UserRepository, WardrobeRepository, WeatherRepository,
)

from domain.services.outfit_builder import OutfitBuilder
from domain.services.take_with_builder import TakeWithBuilder


@dataclass
class DailyRecommendationResult:
    success: bool
    message_key: str      # "success", "not_found"
    take_with: Optional[TakeWith] = None
    outfits: Optional[List[Outfit]] = None


class DailyRecommendation:
    """
    Use-case: построение ежедневной рекомендации.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        wardrobe_repo: WardrobeRepository,
        weather_repo: WeatherRepository,
        outfit_builder: OutfitBuilder,
        take_with_builder: TakeWithBuilder,
    ):
        self._user_repo = user_repo
        self._wardrobe_repo = wardrobe_repo
        self._weather_repo = weather_repo
        self._outfit_builder = outfit_builder
        self._take_with_builder = take_with_builder

    def run(
        self,
        user_id: int,
        today: date,
        count_max: int = 1,
    ) -> DailyRecommendationResult:
        # 1. Получаем пользователя
        user = self._user_repo.get(user_id)
        if user is None:
            return DailyRecommendationResult(
                success=False,
                message_key="not_found"
            )

        # 2. Получаем гардероб
        wardrobe = self._wardrobe_repo.get_user_wardrobe(user_id)

        # 3. Получаем погоду
        weather = self._weather_repo.get_weather(
            date=today,
            city=user.location,
        )

        # 4. Строим аутфиты через доменный сервис
        outfits = self._outfit_builder.build(
            user=user,
            wardrobe=wardrobe,
            weather=weather,
            style=None,
            count_max=count_max,
        )

        # 5. Получаем рекомендации, что взять с собой
        take_with = self._take_with_builder.build(weather)

        return DailyRecommendationResult(
            success=True,
            message_key="success",
            take_with=take_with,
            outfits=outfits
        )
