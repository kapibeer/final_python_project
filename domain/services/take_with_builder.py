from domain import WeatherSnap, TakeWith
from typing import List, Callable
from datetime import datetime


class TakeWithBuilder:
    def __init__(self):
        self.rules: List[Callable[[WeatherSnap, TakeWith], None]] = [
            self._apply_sunny_hot_rules,
            self._apply_precipitation_rules,
            self._apply_wind_rules,
            self._apply_cold_rules,
            self._apply_humidity_rules,
            self._apply_fog_rules,
            self._apply_cloudy_rules,
            self._apply_evening_cooling_rules
        ]
    
    def _get_season(self, date_str: str) -> str:
        """Определяем сезон по дате"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            month = date.month
            
            if month in [12, 1, 2]:
                return "winter"
            elif month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            elif month in [9, 10, 11]:
                return "autumn"
        except (ValueError, TypeError):
            pass
        
        return "unknown"
    
    def build(self, weather: WeatherSnap) -> TakeWith:
        rec = TakeWith(items=[])
        for rule in self.rules:
            rule(weather, rec)
        
        return rec
    
    def _apply_sunny_hot_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для солнечной/жаркой погоды"""
        if weather.is_sunny or weather.temperatures.day >= 25:
            rec.add("головной убор")
            rec.add("солнцезащитные очки")
            if weather.is_uv_high:
                rec.add("SPF")
    
    def _apply_precipitation_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для осадков"""
        if weather.is_rain:
            rec.add("зонт")
            rec.add("дождевик")

        if weather.is_storm:
            rec.add("дождевик")
    
    def _apply_wind_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для ветреной погоды"""
        if weather.is_windy:
            rec.add("ветровка")
    
    def _apply_cold_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для холодной погоды"""
        temps = weather.temperatures
        is_cold = any([
            temps.morning < 10,
            temps.day < 10,
            temps.evening < 10
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
    
    def _apply_cloudy_rules(self, weather: WeatherSnap, rec: TakeWith):
        """Правила для облачной погоды без осадков"""
        if (weather.is_cloudy and 
            not weather.is_rain and 
            not weather.is_snow and 
            not weather.is_sleet):
            rec.add("легкая куртка")
    
    def _apply_evening_cooling_rules(self, weather: WeatherSnap, rec: TakeWith):
        """
        Правила для вечернего похолодания весной, летом и осенью.
        Если вечером заметно прохладнее, чем днем - советуем взять что-то накинуть.
        """
        season = self._get_season(weather.date)
        if season in ["spring", "summer", "autumn"]:
            day_temp = weather.temperatures.day
            evening_temp = weather.temperatures.evening
            temperature_diff = day_temp - evening_temp
            if season == "spring" and temperature_diff >= 8:
                rec.add("легкая куртка/кофта")
                rec.add("шарф")
            
            elif season == "summer" and temperature_diff >= 10:
                rec.add("легкая кофта/толстовка")
            
            elif season == "autumn" and temperature_diff >= 7:
                rec.add("теплый свитер/кофта/куртка")
                rec.add("шапка")
                rec.add("перчатки")
