from dataclasses import dataclass
from typing import List, Optional
from domain import Season, User
from domain import UserRepository, WeatherRepository
from domain.services.detect_season import detect_season
from datetime import date


@dataclass
class SeasonMailResult:
    user_id: int
    season: Optional[Season]


class SeasonMailing:
    """
    Use-case сезонной рассылки.
    Решает, кому отправлять сезонное уведомление и какого оно типа.
    """

    def __init__(self, user_repo: UserRepository,
                 weather_repo: WeatherRepository):
        self._user_repo = user_repo
        self._weather_repo = weather_repo

    def run(self) -> List[SeasonMailResult]:
        results: List[SeasonMailResult] = []

        # текущая дата для запросов в погодный репозиторий
        today = date.today()

        # Берём всех пользователей, у кого включены сезонные уведомления
        users: List[User] = self._user_repo.\
            get_all_users_with_seasonal_notifications()

        for user in users:
            # Получаем погоду для города пользователя
            weather = self._weather_repo.get_weather(today=today,
                                                     city=user.location)

            # Определяем сезон по погоде пользователя
            current_season: Optional[Season] = detect_season(weather)
            if current_season is None:
                continue
            # Если этому пользователю уже отправляли
            # уведомление для этого сезона — пропускаем
            if user.last_season_notified == current_season:
                continue

            results.append(
                SeasonMailResult(
                    user_id=user.id,
                    season=current_season,
                )
            )

            # Обновляем пользователя: помечаем, что ему этот сезон уже отослали
            user.last_season_notified = current_season
            self._user_repo.update(user)

        return results
