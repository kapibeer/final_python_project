from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from domain.models.outfit import Outfit
from domain.models.clothing_item import Style
from domain.models.weather_snap import WeatherSnap
from domain.repositories.user_repository import UserRepository
from domain.repositories.wardrobe_repository import WardrobeRepository
from domain.repositories.weather_repository import WeatherRepository

from domain.services.outfit_builder import OutfitBuilder
from domain.services.weather_classifier import classify_weather
from .weather_summary import WeatherSummary


@dataclass
class BuildOutfitResult:
    success: bool
    message_key: str      # "success", "not_found", "empty_wardrobe"
    outfits: Optional[List[Outfit]] = None
    weather: Optional[WeatherSummary] = None
    style_used: Optional[Style] = None


class BuildOutfit:
    """
    Use-case: подбор аутфита по запросу.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        wardrobe_repo: WardrobeRepository,
        weather_repo: WeatherRepository,
        outfit_builder: OutfitBuilder,
    ):
        self._user_repo = user_repo
        self._wardrobe_repo = wardrobe_repo
        self._weather_repo = weather_repo
        self._outfit_builder = outfit_builder

    def run(
        self,
        user_id: int,
        today: date,
        city: Optional[str] = None,
        style: Optional[Style] = None,
        count_max: int = 1,
    ) -> BuildOutfitResult:

        user = self._user_repo.get(user_id)
        if user is None:
            return BuildOutfitResult(
                success=False,
                message_key="not_found"
            )

        wardrobe = self._wardrobe_repo.get_user_wardrobe(user_id)
        if not wardrobe:
            return BuildOutfitResult(
                success=False,
                message_key="empty_wardrobe"
            )

        location = city or user.location
        weather: Optional[WeatherSnap] = self._weather_repo.get_weather(
            required_date=today,
            city=location,
        )

        if weather is not None:
            coldness = classify_weather(weather)

            outfits = self._outfit_builder.build(
                user=user,
                wardrobe=wardrobe,
                weather=weather,
                style=style,
                count_max=count_max,
            )

            weather_summary = WeatherSummary(
                city=location,
                required_date=today,
                temp_morning=int(weather.temperatures.morning),
                temp_day=int(weather.temperatures.day),
                temp_evening=int(weather.temperatures.evening),
                is_rain=weather.is_rain,
                is_snow=weather.is_snow,
                is_windy=weather.is_windy,
                coldness_level=coldness,
            )

            return BuildOutfitResult(
                success=True,
                message_key="success",
                outfits=outfits,
                weather=weather_summary,
                style_used=style or user.favourite_style,
            )
        return BuildOutfitResult(
                success=False,
                message_key=""
            )
