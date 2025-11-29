from dataclasses import dataclass
from typing import List
from domain import Season


@dataclass
class User:
    user_id: int
    username: str
    gender: str
    age: int
    location: str
    cold_sensitivity: str
    notification_time: str   # "08:00"
    notifications_enabled: bool = True
    season_notifications_enabled: bool = True
    last_season_notifiied: Season
    taste_embedding: List[float]
