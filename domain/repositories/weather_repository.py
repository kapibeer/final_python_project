from typing import Protocol
from domain.models.weather_snap import WeatherSnap
from datetime import date


class WeatherRepository(Protocol):
    def get_weather(self, today: date, city: str) -> WeatherSnap:
        """Вернуть погоду в городе"""
        ...
