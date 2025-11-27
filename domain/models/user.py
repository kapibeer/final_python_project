from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    username: str
    gender: str
    age: int
    location: str
    style: str
    cold_sensitivity: str    # "high" / "normal" / "low"

    notification_time: str   # "08:00"
    notifications_enabled: bool = True
