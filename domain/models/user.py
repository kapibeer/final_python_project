from dataclasses import dataclass
from typing import List


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
    taste_embedding: List[float]
