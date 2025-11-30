from typing import Protocol
from domain import WeatherSnap
from datetime import date


class WeatherRepository(Protocol):
    def get_weather(self, today: date, city: str) -> WeatherSnap:
        """Вернуть погоду в городе"""
        ...
