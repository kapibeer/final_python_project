from dataclasses import dataclass
from datetime import date


@dataclass
class TemperaturePeriod:
    morning: float
    day: float
    evening: float


@dataclass
class WeatherSnap:
    location: str
    required_date: date

    temperatures: TemperaturePeriod

    is_rain: bool = False             # идёт дождь
    is_snow: bool = False             # идёт снег
    is_sleet: bool = False            # мокрый снег
    is_storm: bool = False            # гроза / шторм / буря
    is_windy: bool = False            # сильный ветер
    is_uv_high: bool = False          # нужен SPF
    is_humid: bool = False            # высокая влажность (ощущается уже иначе)
    is_sunny: bool = False            # солнечно ли
    is_fog: bool = False              # есть ли туман
    is_cloudy: bool = False           # облачно ли
