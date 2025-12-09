# domain/__init__.py
# flake8: noqa

# МОДЕЛИ
from .models.clothing_item import (
    ClothingItem,
    Style,
    TopGroup,
    ClothingCategory,
    Color,
    ClothingSubtype,
    WarmthLevel,
    SUBTYPE_TO_TOP_GROUP,
)
from .models.outfit import Outfit
from .models.take_with import TakeWith
from .models.season import Season
from .models.user import User
from .models.weather_snap import WeatherSnap, TemperaturePeriod

# ПРОТОКОЛЫ РЕПОЗИТОРИЕВ
from .repositories.user_repository import UserRepository
from .repositories.wardrobe_repository import WardrobeRepository
from .repositories.weather_repository import WeatherRepository

__all__ = [
    # модели
    "ClothingItem",
    "Style",
    "TopGroup",
    "ClothingCategory",
    "Color",
    "ClothingSubtype",
    "WarmthLevel",
    "SUBTYPE_TO_TOP_GROUP",
    "Outfit",
    "TakeWith",
    "User",
    "Season",
    "WeatherSnap",
    "TemperaturePeriod",
    # репозитории
    "UserRepository",
    "WardrobeRepository",
    "WeatherRepository",
]