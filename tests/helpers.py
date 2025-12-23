from datetime import date, time
from typing import List, Optional, Dict
from domain.models.weather_snap import WeatherSnap, TemperaturePeriod
from domain.models.user import User, ColdSensitivity
from domain.models.take_with import TakeWith
from domain.models.outfit import Outfit
from domain.models.clothing_item import (
    ClothingItem,
    ClothingCategory,
    ClothingSubtype,
    Color,
    Style,
    WarmthLevel,
)
from domain.repositories.user_repository import UserRepository
from domain.repositories.weather_repository import WeatherRepository
from domain.services.outfit_builder import OutfitBuilder
from domain.services.take_with_builder import TakeWithBuilder


def make_weather(
    d: date,
    *,
    morning: float,
    day: float,
    evening: float,
    is_rain: bool = False,
    is_snow: bool = False,
    is_sleet: bool = False,
    is_storm: bool = False,
    is_windy: bool = False,
    is_uv_high: bool = False,
    is_humid: bool = False,
    is_sunny: bool = False,
    is_fog: bool = False,
    is_cloudy: bool = False,
    city: str = "TestCity",
) -> WeatherSnap:
    temps = TemperaturePeriod(morning=morning, day=day, evening=evening)
    return WeatherSnap(
        location=city,
        required_date=d,
        temperatures=temps,
        is_rain=is_rain,
        is_snow=is_snow,
        is_sleet=is_sleet,
        is_storm=is_storm,
        is_windy=is_windy,
        is_uv_high=is_uv_high,
        is_humid=is_humid,
        is_sunny=is_sunny,
        is_fog=is_fog,
        is_cloudy=is_cloudy,
    )


def make_user(cs: ColdSensitivity = ColdSensitivity.MEDIUM) -> User:
    return User(
        user_id=1,
        username="test",
        gender="female",
        age=20,
        location="TestCity",
        cold_sensitivity=cs,
        notifications_enabled=True,
        season_notifications_enabled=True,
        last_season_notifiied=None,
        favourite_style=Style.CASUAL,
    )


def make_item(
    *,
    item_id: int,
    category: ClothingCategory,
    subtype: ClothingSubtype,
    warmth: WarmthLevel = WarmthLevel.MEDIUM,
    is_waterproof: bool = False,
    is_windproof: bool = False,
) -> ClothingItem:
    return ClothingItem(
        item_id=item_id,
        owner_id=1,
        image_id="img",
        name="x",
        category=category,
        main_color=Color.BLACK,
        style=Style.CASUAL,
        warmth_level=warmth,
        subtype=subtype,
        is_waterproof=is_waterproof,
        is_windproof=is_windproof,
    )


class FakeUserRepo(UserRepository):
    def __init__(self, users: list[User]):
        self.users = users
        self.updated: list[User] = []

    async def get_all_users_with_seasonal_notifications(self) -> List[User]:
        return self.users

    async def update(self, user: User) -> None:
        self.updated.append(user)

    # --- методы, которые протокол требует, но в этих тестах не нужны ---

    async def get(self, user_id: int) -> Optional[User]:
        for u in self.users:
            if u.user_id == user_id:
                return u
        return None

    async def create(self, user: User) -> None:
        self.users.append(user)

    async def delete(self, user_id: int) -> None:
        self.users = [u for u in self.users if u.user_id != user_id]

    async def get_or_create(self, user: User) -> User:
        existing = await self.get(user.user_id)
        if existing is not None:
            return existing
        await self.create(user)
        return user

    async def get_users_to_notify_between(self, start: time, end: time) \
            -> list[User]:
        raise NotImplementedError


class FakeWeatherRepo(WeatherRepository):
    def __init__(self, weather_by_city: dict[str, Optional[WeatherSnap]]):
        self.weather_by_city = weather_by_city

    def get_weather(self, required_date: date, city: str) \
            -> Optional[WeatherSnap]:
        return self.weather_by_city.get(city)


class FakeWardrobeRepo:
    def __init__(self, items: Optional[List[ClothingItem]] = None):
        self.items: Dict[int, ClothingItem] = {
            i.item_id: i for i in (items or [])
        }

        self.added: List[ClothingItem] = []
        self.updated: List[ClothingItem] = []
        self.deleted: List[int] = []

    async def get_item(self, user_id: int, item_id: int) \
            -> Optional[ClothingItem]:
        return self.items.get(item_id)

    async def get_user_wardrobe(self, user_id: int) -> List[ClothingItem]:
        return [i for i in self.items.values() if i.owner_id == user_id]

    async def add_item(self, user_id: int, item: ClothingItem) -> int:
        self.items[item.item_id] = item
        self.added.append(item)
        return item.item_id

    async def update_item(self, user_id: int, item: ClothingItem) -> None:
        self.items[item.item_id] = item
        self.updated.append(item)

    async def delete_item(self, user_id: int, item_id: int) -> None:
        self.items.pop(item_id, None)
        self.deleted.append(item_id)


class FakeOutfitBuilder(OutfitBuilder):
    def __init__(self, outfits: List[Outfit]):
        self._outfits = outfits

    def build(self, **kwargs):  # type: ignore
        return list(self._outfits)


class FakeTakeWithBuilder(TakeWithBuilder):
    def __init__(self, items: Optional[List[str]] = None):
        self._items = items if items is not None else []

    def build(self, weather: WeatherSnap) -> TakeWith:
        return TakeWith(items=list(self._items))
