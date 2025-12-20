from typing import Protocol, Optional
from domain.models.weather_snap import WeatherSnap
from datetime import date


class WeatherRepository(Protocol):
    def get_weather(self, required_date: date, city: str) \
            -> Optional[WeatherSnap]:
        """Вернуть погоду в городе"""
        ...
