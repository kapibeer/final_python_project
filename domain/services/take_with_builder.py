from domain.models.weather_snap import WeatherSnap
from domain.models.take_with import TakeWith
from typing import List, Callable
from datetime import date


class TakeWithBuilder:
    def __init__(self):
        self.rules: List[Callable[[WeatherSnap, TakeWith], None]] = [
            self._apply_sunny_hot_rules,
            self._apply_precipitation_rules,
            self._apply_wind_rules,
            self._apply_cold_rules,
            self._apply_humidity_rules,
            self._apply_fog_rules,
            self._apply_evening_cooling_rules
        ]

    def _get_season(self, required_date: date) -> str:
        """Определяем сезон по дате"""
        month = required_date.month

        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        return "unknown"

    def build(self, weather: WeatherSnap) -> TakeWith:
        rec = TakeWith(items=[])
        for rule in self.rules:
            rule(weather, rec)

        return rec

    def _apply_sunny_hot_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для солнечной/жаркой погоды"""
        if weather.is_sunny and weather.temperatures.day >= 20:
            rec.add("головной убор")
            rec.add("солнцезащитные очки")
            if weather.is_uv_high:
                rec.add("SPF")

    def _apply_precipitation_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для осадков"""
        if weather.is_storm:
            rec.add("дождевик")
            return

        if weather.is_rain:
            rec.add("зонт")

    def _apply_wind_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для ветреной погоды"""
        if weather.is_windy:
            rec.add("ветровка")

    def _apply_cold_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для холодной погоды"""
        temps = weather.temperatures
        is_cold = any([
            temps.morning < 4,
            temps.day < 7,
            temps.evening < 3
        ])

        if is_cold:
            rec.add("шапка")
            rec.add("шарф")
            rec.add("перчатки/варежки")

    def _apply_humidity_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для высокой влажности"""
        if weather.is_humid and weather.temperatures.day < 20:
            rec.add("легкая непромокаемая куртка")

    def _apply_fog_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для тумана"""
        if weather.is_fog:
            rec.add("светоотражающие элементы")

    def _apply_evening_cooling_rules(self, weather: WeatherSnap,
                                     rec: TakeWith):
        """
        Правила для вечернего похолодания весной, летом и осенью.
        Если вечером заметно прохладнее, чем днем - советуем взять
        что-то накинуть.
        """
        season = self._get_season(weather.required_date)
        morning_temp = weather.temperatures.morning
        day_temp = weather.temperatures.day
        evening_temp = weather.temperatures.evening
        avg = (morning_temp + day_temp + evening_temp) / 3
        if "легкая непромокаемая куртка" in rec.items:
            return
        if season in ["spring", "summer", "autumn"] or avg >= 10:
            morning_temp = weather.temperatures.morning
            day_temp = weather.temperatures.day
            evening_temp = weather.temperatures.evening
            temperature_diff = max(day_temp - evening_temp,
                                   day_temp - morning_temp)
            if season == "spring":
                if day_temp >= 15 and temperature_diff >= 5:
                    rec.add("легкая куртка")
            elif season == "summer":
                if day_temp >= 20 and temperature_diff >= 7:
                    rec.add("легкая кофта")
            elif season == "autumn":
                if day_temp >= 15 and temperature_diff >= 5:
                    rec.add("куртка")
            else:
                if day_temp >= 15 and temperature_diff >= 5:
                    rec.add("куртка")
