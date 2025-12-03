from enum import StrEnum
from dataclasses import dataclass
from domain import Season, Style
from datetime import time


class ColdSensitivity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class User:
    user_id: int
    username: str
    gender: str
    age: int
    location: str
    cold_sensitivity: ColdSensitivity
    notification_time: time
    notifications_enabled: bool = True
    season_notifications_enabled: bool = True
    last_season_notifiied: Season
    favourite_style: Style
