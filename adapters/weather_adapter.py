from domain import WeatherRepository
from datetime import date


class OpenWeatherAdapter(WeatherRepository):
    def get_weather(self, today: date, city: str):
        ...
