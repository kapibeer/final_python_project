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
    date: date

    temperatures: TemperaturePeriod

    is_rain: bool              # идёт дождь
    is_snow: bool              # идёт снег
    is_sleet: bool             # мокрый снег
    is_storm: bool             # гроза / шторм / буря
    is_windy: bool             # сильный ветер
    is_uv_high: bool           # нужен SPF
    is_humid: bool             # высокая влажность (ощущается уже иначе)
    is_sunny: bool             # солнечно ли
    is_fog: bool               # есть ли туман
    is_cloudy: bool            # облачно ли
