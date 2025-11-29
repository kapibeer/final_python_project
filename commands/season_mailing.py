from dataclasses import dataclass
from typing import List
from domain import Season, User, WeatherSnap
from domain import UserRepository
from domain import detect_season


@dataclass
class SeasonMailResult:
    user_id: int
    season: Season


class SeasonMailing:
    """
    Use-case сезонной рассылки.
    Решает, кому отправлять сезонное уведомление и какого оно типа.
    """

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def run(self, weather: WeatherSnap) -> List[SeasonMailResult]:
        current_season: Season = detect_season(weather)
        results: List[SeasonMailResult] = []

        # Берём всех пользователей, у кого включены сезонные уведомления
        users: List[User] = self._user_repo.\
            get_all_users_with_seasonal_notifications()

        for user in users:
            # Если этому пользователю уже отправляли
            # уведомление для этого сезона — пропускаем
            if user.last_season_notified == current_season:
                continue

            # Добавляем задачу на отправку
            results.append(
                SeasonMailResult(
                    user_id=user.id,
                    season=current_season
                )
            )

            # Обновляем пользователя: помечаем, что ему этот сезон уже отослали
            user.last_season_notified = current_season
            self._user_repo.update(user)

        pass
