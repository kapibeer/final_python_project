import pytest
from datetime import date

from commands.daily_recommendation import DailyRecommendation
from domain.models.clothing_item import ClothingCategory, ClothingSubtype
from domain.models.outfit import Outfit

from tests.helpers import make_user, make_weather, make_item
from tests.helpers import (
    FakeUserRepo,
    FakeWardrobeRepo,
    FakeWeatherRepo,
    FakeOutfitBuilder,
    FakeTakeWithBuilder,
)


@pytest.mark.asyncio
async def test_daily_not_found_when_user_missing() -> None:
    # user_repo без пользователей
    user_repo = FakeUserRepo(users=[])
    wardrobe_repo = FakeWardrobeRepo(items=[])
    weather_repo = FakeWeatherRepo({"TestCity": make_weather(date.today(),
                                                             morning=0, day=5,
                                                             evening=0)})
    outfit_builder = FakeOutfitBuilder(outfits=[])
    take_with_builder = FakeTakeWithBuilder(items=["зонт"])

    usecase = DailyRecommendation(
        user_repo=user_repo,
        wardrobe_repo=wardrobe_repo,
        weather_repo=weather_repo,
        outfit_builder=outfit_builder,
        take_with_builder=take_with_builder,
    )

    res = await usecase.run(user_id=123, today=date.today())

    assert res.success is False
    assert res.message_key == "not_found"
    assert res.weather is None
    assert res.outfit is None
    assert res.take_with is None
    assert res.style_used is None


@pytest.mark.asyncio
async def test_daily_returns_success_if_outfit_empty_but_weather_exists() \
        -> None:
    user = make_user()
    w = make_weather(date.today(), morning=10, day=12,
                     evening=9, is_windy=True)

    user_repo = FakeUserRepo(users=[user])
    wardrobe_repo = FakeWardrobeRepo(items=[])
    weather_repo = FakeWeatherRepo({user.location: w})
    outfit_builder = FakeOutfitBuilder(outfits=[])
    take_with_builder = FakeTakeWithBuilder(items=["ветровка"])

    usecase = DailyRecommendation(
        user_repo=user_repo,
        wardrobe_repo=wardrobe_repo,
        weather_repo=weather_repo,
        outfit_builder=outfit_builder,
        take_with_builder=take_with_builder,
    )

    res = await usecase.run(user_id=user.user_id, today=date.today())

    assert res.success is True
    assert res.message_key == "success"

    assert res.weather is not None
    assert res.weather.city == user.location
    assert res.weather.is_windy is True

    assert res.outfit is None

    assert res.take_with is not None
    assert "ветровка" in res.take_with.items

    assert res.style_used == user.favourite_style


@pytest.mark.asyncio
async def test_daily_returns_outfit_when_builder_returns_one() -> None:
    user = make_user()
    w = make_weather(date.today(), morning=0, day=4, evening=0, is_rain=True)

    # гардероб не обязателен для фейкового outfit_builder, но положим 1 вещь
    item = make_item(
        item_id=1,
        category=ClothingCategory.BOTTOM,
        subtype=ClothingSubtype.JEANS,
    )
    outfit = Outfit(items=[item])

    user_repo = FakeUserRepo(users=[user])
    wardrobe_repo = FakeWardrobeRepo(items=[item])
    weather_repo = FakeWeatherRepo({user.location: w})
    outfit_builder = FakeOutfitBuilder(outfits=[outfit])
    take_with_builder = FakeTakeWithBuilder(items=["зонт"])

    usecase = DailyRecommendation(
        user_repo=user_repo,
        wardrobe_repo=wardrobe_repo,
        weather_repo=weather_repo,
        outfit_builder=outfit_builder,
        take_with_builder=take_with_builder,
    )

    res = await usecase.run(user_id=user.user_id, today=date.today())

    assert res.success is True
    assert res.message_key == "success"

    assert res.outfit is not None
    assert len(res.outfit.items) == 1
    assert res.outfit.items[0].item_id == 1

    assert res.weather is not None
    assert res.weather.is_rain is True

    assert res.take_with is not None
    assert res.take_with.items == ["зонт"]


@pytest.mark.asyncio
async def test_daily_returns_failure_when_weather_is_none() -> None:
    user = make_user()
    user_repo = FakeUserRepo(users=[user])
    wardrobe_repo = FakeWardrobeRepo(items=[])
    weather_repo = FakeWeatherRepo({user.location: None})
    outfit_builder = FakeOutfitBuilder(outfits=[])
    take_with_builder = FakeTakeWithBuilder(items=["что-то"])

    usecase = DailyRecommendation(
        user_repo=user_repo,
        wardrobe_repo=wardrobe_repo,
        weather_repo=weather_repo,
        outfit_builder=outfit_builder,
        take_with_builder=take_with_builder,
    )

    res = await usecase.run(user_id=user.user_id, today=date.today())

    assert res.success is False
    assert res.message_key == ""
    assert res.weather is None
    assert res.outfit is None
    assert res.take_with is None
    assert res.style_used is None
