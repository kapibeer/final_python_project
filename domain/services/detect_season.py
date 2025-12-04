from domain import Season, WeatherSnap
from datetime import datetime, timedelta
from typing import Optional, Dict


class SeasonChangeDetector:
    """
    Отслеживает момент для отправки уведомлений о смене сезона.
    Отправляет уведомления за 1-2 недели до начала сезона.
    """
    
    def __init__(self):
        self.season_start_dates = {
            Season.SPRING: self._get_spring_start_date,
            Season.SUMMER: self._get_summer_start_date,
            Season.AUTUMN: self._get_autumn_start_date,
            Season.WINTER: self._get_winter_start_date,
        }

        self.last_notification_dates: Dict[Season, Optional[datetime]] = {
            Season.SPRING: None,
            Season.SUMMER: None,
            Season.AUTUMN: None,
            Season.WINTER: None,
        }
    
    def _get_spring_start_date(self, year: int) -> datetime:
        """Метеорологическая весна начинается 1 марта"""
        return datetime(year, 3, 1)
    
    def _get_summer_start_date(self, year: int) -> datetime:
        """Метеорологическое лето начинается 1 июня"""
        return datetime(year, 6, 1)
    
    def _get_autumn_start_date(self, year: int) -> datetime:
        """Метеорологическая осень начинается 1 сентября"""
        return datetime(year, 9, 1)
    
    def _get_winter_start_date(self, year: int) -> datetime:
        """Метеорологическая зима начинается 1 декабря"""
        return datetime(year, 12, 1)
    
    def check_season_change_notification(self, weather: WeatherSnap) -> Optional[Season]:
        """
        Проверяет, пора ли отправлять уведомление о смене сезона.
        Возвращает Season, если пора отправлять уведомление, иначе None.
        """
        try:
            current_date = self._parse_date(weather.date)
            if not current_date:
                return None

            current_season = self._get_season_by_date(current_date)
            next_season = self._get_next_season(current_season)
            season_start_date = self.season_start_dates[next_season](current_date.year)
            if current_date > season_start_date:
                season_start_date = self.season_start_dates[next_season](current_date.year + 1)
            two_weeks_before = season_start_date - timedelta(days=14)
            one_week_before = season_start_date - timedelta(days=7)
            in_notification_window = (
                two_weeks_before <= current_date <= one_week_before
            )
            last_notification = self.last_notification_dates[next_season]
            already_notified_this_year = (
                last_notification and 
                last_notification.year == current_date.year
            )
            if in_notification_window and not already_notified_this_year:
                self.last_notification_dates[next_season] = current_date
                return next_season
            if self._weather_matches_season(weather, next_season):
                if not already_notified_this_year:
                    self.last_notification_dates[next_season] = current_date
                    return next_season
            
            return None
            
        except Exception as e:
            print(f"Error checking season change: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Парсит дату из строки"""
        formats = ["%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def _get_season_by_date(self, date: datetime) -> Season:
        """Определяет сезон по дате"""
        month = date.month
        if month in [12, 1, 2]:
            return Season.WINTER
        elif month in [3, 4, 5]:
            return Season.SPRING
        elif month in [6, 7, 8]:
            return Season.SUMMER
        else:  # 9, 10, 11
            return Season.AUTUMN
    
    def _get_next_season(self, current_season: Season) -> Season:
        """Возвращает следующий сезон"""
        seasons_order = [Season.WINTER, Season.SPRING, Season.SUMMER, Season.AUTUMN]
        current_index = seasons_order.index(current_season)
        next_index = (current_index + 1) % len(seasons_order)
        return seasons_order[next_index]
    
    def _weather_matches_season(self, weather: WeatherSnap, season: Season) -> bool:
        """Проверяет, соответствует ли погода сезону"""
        temps = weather.temperatures
        
        if season == Season.WINTER:
            return (weather.is_snow or temps.day < 0 or 
                   (temps.day < 5 and weather.is_windy))
        
        elif season == Season.SPRING:
            return (weather.is_rain and 
                   temps.morning < 10 and 
                   temps.day >= 10 and
                   not weather.is_snow)
        
        elif season == Season.SUMMER:
            return (weather.is_sunny and 
                   temps.day >= 20 and 
                   weather.is_uv_high)
        
        elif season == Season.AUTUMN:
            return (weather.is_rain and 
                   weather.is_windy and 
                   temps.day < 15 and
                   not weather.is_snow)
        
        return False


def detect_season(weather: WeatherSnap) -> Season:
    """
    Определяет, пора ли отправлять уведомление о смене сезона.
    Эта функция обертка для обратной совместимости.
    """
    detector = SeasonChangeDetector()
    return detector.check_season_change_notification(weather)