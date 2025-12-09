from domain import Season, WeatherSnap
from datetime import date, timedelta
from typing import Optional


class SeasonChangeDetector:
    """
    Отслеживает момент для отправки уведомлений о смене сезона.
    """

    def __init__(self):
        self.season_starts = {
            Season.SPRING: (3, 1),
            Season.SUMMER: (6, 1),
            Season.AUTUMN: (9, 1),
            Season.WINTER: (12, 1),
        }

    def check_season_change_notification(self, weather: WeatherSnap) \
            -> Optional[Season]:
        """
        Проверяет, пора ли отправлять уведомление о смене сезона.
        Возвращает следующий сезон, если пора, иначе None.
        """
        today = weather.today

        season_today = self._get_season_start_if_today(today)
        if season_today is not None:
            return season_today

        for season in Season:
            if self._should_notify_about_season(today, weather, season):
                return season

        return None

    def _get_season_start_if_today(self, today: date) -> Optional[Season]:
        """
        Возвращает сезон, который начинается сегодня, или None.
        """
        month, day = today.month, today.day
        for season, (start_month, start_day) in self.season_starts.items():
            if month == start_month and day == start_day:
                return season
        return None

    def _should_notify_about_season(
        self,
        today: date,
        weather: WeatherSnap,
        target_season: Season,
    ) -> bool:
        """
        Проверяет, нужно ли уведомлять о конкретном сезоне.
        """
        month_start, day_start = self.season_starts[target_season]
        year = today.year
        if target_season == Season.SPRING and today.month == 12:
            year += 1

        season_start = date(year, month_start, day_start)
        three_weeks_before = season_start - timedelta(days=21)

        if not (three_weeks_before <= today <= season_start):
            return False

        return self._has_season_signs(weather, target_season)

    def _has_season_signs(self, weather: WeatherSnap, season: Season) -> bool:
        """
        Проверяет, есть ли признаки приближающегося сезона.
        """
        temps = weather.temperatures

        if season == Season.SPRING:
            signs = [
                temps.day >= 0,
                not weather.is_snow,
                weather.is_rain or weather.is_sleet,
                temps.day - temps.morning >= 5,
                weather.is_sunny and temps.day >= 5,
            ]
            return sum(signs) >= 2

        elif season == Season.SUMMER:
            signs = [
                temps.day >= 18,
                weather.is_sunny,
                not weather.is_rain,
                weather.is_uv_high,
                temps.evening >= 15,
            ]
            return sum(signs) >= 2

        elif season == Season.AUTUMN:
            signs = [
                temps.day < 20,
                weather.is_rain,
                weather.is_windy,
                weather.is_cloudy,
                weather.is_humid,
            ]
            return sum(signs) >= 2

        elif season == Season.WINTER:
            signs = [
                temps.day < 5,
                weather.is_snow or weather.is_sleet,
                temps.morning < 0,
                weather.is_windy and temps.day < 10,
                not weather.is_rain and temps.day < 8,
            ]
            return sum(signs) >= 2

        return False


def detect_season(weather: WeatherSnap) -> Optional[Season]:
    """
    Основная функция для определения,
    пора ли отправлять уведомление о смене сезона.
    """
    detector = SeasonChangeDetector()
    return detector.check_season_change_notification(weather)
