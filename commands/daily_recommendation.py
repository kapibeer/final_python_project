from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain import (
    Outfit, TakeWith,
    UserRepository, WardrobeRepository, WeatherRepository, Style
)
from domain.services.outfit_builder import OutfitBuilder
from domain.services.take_with_builder import TakeWithBuilder
from .weather_summary import WeatherSummary
from domain.services.weather_classifier import classify_weather


@dataclass
class DailyRecommendationResult:
    success: bool
    message_key: str      # "success", "not_found"
    outfit: Optional[Outfit] = None
    weather: Optional[WeatherSummary] = None
    style_used: Optional[Style] = None
    take_with: Optional[TakeWith] = None


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
            count_max=1,
        )
        outfit = None
        if outfits:
            outfit = outfits[0]

        # 4. Сводка погоды
        coldness = classify_weather(weather)
        weather_summary = WeatherSummary(
            city=user.location,
            date=today,
            temp_morning=int(weather.temperatures.morning),
            temp_day=int(weather.temperatures.day),
            temp_evening=int(weather.temperatures.evening),
            is_rain=weather.is_rain,
            is_snow=weather.is_snow,
            is_windy=weather.is_windy,
            coldness_level=coldness,
        )

        # 5. Получаем рекомендации, что взять с собой
        take_with = self._take_with_builder.build(weather)

        return DailyRecommendationResult(
            success=True,
            message_key="success",
            take_with=take_with,
            outfit=outfit,
            weather=weather_summary
        )
