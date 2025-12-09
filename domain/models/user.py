from enum import StrEnum
from dataclasses import dataclass
from .season import Season
from .clothing_item import Style
from datetime import time
from typing import Optional


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
    cold_sensitivity: ColdSensitivity = ColdSensitivity.MEDIUM
    notification_time: time = time(hour=10, minute=00)
    notifications_enabled: bool = True
    season_notifications_enabled: bool = True
    last_season_notifiied: Optional[Season] = None
    favourite_style: Style = Style.CASUAL
