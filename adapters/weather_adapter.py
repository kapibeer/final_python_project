from datetime import date
from typing import Optional
import requests
from domain.models.weather_snap import WeatherSnap, TemperaturePeriod
from domain.repositories.weather_repository import WeatherRepository


class OpenWeatherAdapter(WeatherRepository):
    """
    Адаптер для получения погоды - weatherapi.com
    """

    def __init__(self) -> None:
        self.api_key: str = "86fbe05ab103488bb7b192102250812"
        self.base_url: str = "https://api.weatherapi.com/v1/forecast.json"

    def get_weather(self, required_date: date, city: str) \
            -> Optional[WeatherSnap]:
        today = date.today()
        step_days = (required_date - today).days

        if step_days < 0 or step_days >= 14:
            return None

        params = {
            "key": self.api_key,
            "q": city,
            "lang": "en",
            "days": step_days + 1,
            "aqi": "no",
            "alerts": "no"
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            forecast_days = response.json()
            data = forecast_days['forecast']['forecastday'][step_days]
        except Exception:
            return None

        temperatures = TemperaturePeriod(
            morning=data['hour'][8]['temp_c'],   # 8:00
            day=data['hour'][14]['temp_c'],      # 14:00
            evening=data['hour'][20]['temp_c']   # 20:00
        )

        is_rain: bool = True if max(h['chance_of_rain']
                                    for h in data['hour']) >= 50 else False
        is_snow: bool = True if max(h['chance_of_snow']
                                    for h in data['hour']) >= 50 else False
        is_sleet: bool = any("sleet" in h["condition"]["text"].lower()
                             for h in data['hour'])
        is_storm: bool = any("thunder" in h["condition"]["text"].lower() and
                             "light" not in h["condition"]["text"].lower()
                             for h in data['hour'])
        is_windy: bool = True if data['day']['maxwind_kph'] >= 25 else False
        is_uv_high: bool = True if max(h['uv']
                                       for h in data['hour']) >= 5 else False
        is_humid: bool = True if data['day']['avghumidity'] >= 80 else False
        is_sunny: bool = any("sunny" in h["condition"]["text"].lower() or
                             "clear" in h["condition"]["text"].lower()
                             for h in data['hour'])
        is_fog: bool = any("mist" in h["condition"]["text"].lower() or
                           "fog" in h["condition"]["text"].lower()
                           for h in data['hour'])
        is_cloudy: bool = any("overcast" in h["condition"]["text"].lower() or
                              "cloudy" in h["condition"]["text"].lower()
                              for h in data['hour'])

        return WeatherSnap(
            location=city,
            today=required_date,
            temperatures=temperatures,
            is_rain=is_rain,
            is_snow=is_snow,
            is_sleet=is_sleet,
            is_storm=is_storm,
            is_windy=is_windy,
            is_uv_high=is_uv_high,
            is_humid=is_humid,
            is_sunny=is_sunny,
            is_fog=is_fog,
            is_cloudy=is_cloudy
        )
