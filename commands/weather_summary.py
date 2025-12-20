from dataclasses import dataclass
from datetime import date


@dataclass
class WeatherSummary:
    city: str
    required_date: date
    temp_morning: int
    temp_day: int
    temp_evening: int
    is_rain: bool
    is_snow: bool
    is_windy: bool
    coldness_level: int
