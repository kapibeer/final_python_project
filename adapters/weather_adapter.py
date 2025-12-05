from domain import WeatherRepository, WeatherSnap
from datetime import date


class OpenWeatherAdapter(WeatherRepository):
    def get_weather(self, today: date, location: str) -> WeatherSnap:
        ...
