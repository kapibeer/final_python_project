from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from domain import (
    Outfit, Style,
    OutfitBuilder,
    UserRepository, WardrobeRepository, WeatherRepository,
)


@dataclass
class BuildOutfitResult:
    success: bool
    message_key: str      # "success", "not_found"
    outfits: Optional[List[Outfit]] = None


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
        # 1. Получаем пользователя
        user = self._user_repo.get(user_id)
        if user is None:
            return BuildOutfitResult(
                success=False,
                message_key="not_found"
            )

        # 2. Получаем гардероб
        wardrobe = self._wardrobe_repo.get_user_wardrobe(user_id)

        # 3. Определяем локацию
        location = city or user.location

        # 4. Получаем погоду
        weather = self._weather_repo.get_weather(
            date=today,
            city=location,
        )

        # 5. Строим аутфиты через доменный сервис
        outfits = self._outfit_builder.build(
            user=user,
            wardrobe=wardrobe,
            weather=weather,
            style=style,
            count_max=count_max,
        )

        return BuildOutfitResult(
            success=True,
            message_key="success",
            outfits=outfits,
        )
