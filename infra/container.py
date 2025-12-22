# infra/container.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

# --- domain protocols ---
from domain.repositories.user_repository import UserRepository
from domain.repositories.wardrobe_repository import WardrobeRepository
from domain.repositories.weather_repository import WeatherRepository

# --- db adapters (SQLAlchemy repos) ---
from adapters.database_adapters.repositories.db_user_repository \
    import DBUserRepository
from adapters.database_adapters.repositories.db_wardrobe_repository \
    import DBWardrobeRepository
from adapters.weather_adapter import OpenWeatherAdapter

# --- ML / other adapters ---
from adapters.ml.item_recommender import MLItemRecommender

# --- domain services ---
from domain.services.outfit_builder import OutfitBuilder
from domain.services.take_with_builder import TakeWithBuilder

# --- commands/use-cases ---
from commands.build_outfit import BuildOutfit
from commands.daily_recommendation import DailyRecommendation
from commands.manage_wardrobe import ManageWardrobe
from commands.manage_user_preferences import ManageUserPreferences
from commands.season_mailing import SeasonMailing


@dataclass(frozen=True)
class Container:
    """
    DI-контейнер
    """
    session_factory: Callable[[], AsyncSession]

    # -------------------- repositories --------------------

    def user_repo(self) -> UserRepository:
        return DBUserRepository(self.session_factory)

    def wardrobe_repo(self) -> WardrobeRepository:
        return DBWardrobeRepository(self.session_factory)

    def weather_repo(self) -> WeatherRepository:
        return OpenWeatherAdapter()

    # -------------------- adapters / services --------------------

    def item_recommender(self) -> MLItemRecommender:
        return MLItemRecommender()

    def outfit_builder(self) -> OutfitBuilder:
        return OutfitBuilder(recommender=self.item_recommender())

    def take_with_builder(self) -> TakeWithBuilder:
        return TakeWithBuilder()

    # -------------------- use-cases --------------------

    def build_outfit(self) -> BuildOutfit:
        return BuildOutfit(
            user_repo=self.user_repo(),
            wardrobe_repo=self.wardrobe_repo(),
            weather_repo=self.weather_repo(),
            outfit_builder=self.outfit_builder(),
        )

    def daily_recommendation(self) -> DailyRecommendation:
        return DailyRecommendation(
            user_repo=self.user_repo(),
            wardrobe_repo=self.wardrobe_repo(),
            weather_repo=self.weather_repo(),
            outfit_builder=self.outfit_builder(),
            take_with_builder=self.take_with_builder(),
        )

    def manage_wardrobe(self) -> ManageWardrobe:
        return ManageWardrobe(
            wardrobe_repo=self.wardrobe_repo(),
        )

    def manage_user_preferences(self) -> ManageUserPreferences:
        return ManageUserPreferences(
            user_repo=self.user_repo(),
        )

    def season_mailing(self) -> SeasonMailing:
        return SeasonMailing(
            user_repo=self.user_repo(),
            weather_repo=self.weather_repo(),
        )
