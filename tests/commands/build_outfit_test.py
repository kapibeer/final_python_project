import pytest
from datetime import date

from commands.build_outfit import BuildOutfit
from domain.models.outfit import Outfit
from domain.models.clothing_item import Style, ClothingCategory, \
    ClothingSubtype

from tests.helpers import (
    make_user,
    make_weather,
    make_item,
    FakeUserRepo,
    FakeWardrobeRepo,
    FakeWeatherRepo,
    FakeOutfitBuilder,
)


@pytest.mark.asyncio
async def test_build_outfit_not_found_when_user_missing() -> None:
    user_repo = FakeUserRepo(users=[])
    wardrobe_repo = FakeWardrobeRepo(items=[])
    weather_repo = FakeWeatherRepo({"TestCity": make_weather(date.today(),
                                                             morning=0, day=5,
                                                             evening=0)})
    outfit_builder = FakeOutfitBuilder(outfits=[])

    uc = BuildOutfit(
        user_repo=user_repo,
        wardrobe_repo=wardrobe_repo,
        weather_repo=weather_repo,
        outfit_builder=outfit_builder,
    )

    res = await uc.run(user_id=123, today=date.today())

    assert res.success is False
    assert res.message_key == "not_found"
    assert res.outfits is None
    assert res.weather is None
    assert res.style_used is None


@pytest.mark.asyncio
async def test_build_outfit_empty_wardrobe() -> None:
    user = make_user()
    user_repo = FakeUserRepo(users=[user])
    wardrobe_repo = FakeWardrobeRepo(items=[])  # пусто
    weather_repo = FakeWeatherRepo({user.location: make_weather(date.today(),
                                                                morning=0,
                                                                day=5,
                                                                evening=0)})
    outfit_builder = FakeOutfitBuilder(outfits=[])

    uc = BuildOutfit(user_repo, wardrobe_repo, weather_repo, outfit_builder)

    res = await uc.run(user_id=user.user_id, today=date.today())

    assert res.success is False
    assert res.message_key == "empty_wardrobe"
    assert res.outfits is None
    assert res.weather is None
    assert res.style_used is None


@pytest.mark.asyncio
async def test_build_outfit_weather_none_returns_failure() -> None:
    user = make_user()
    item = make_item(
        item_id=1,
        category=ClothingCategory.BOTTOM,
        subtype=ClothingSubtype.JEANS,
    )

    user_repo = FakeUserRepo(users=[user])
    wardrobe_repo = FakeWardrobeRepo(items=[item])
    weather_repo = FakeWeatherRepo({user.location: None})  # погоды нет
    outfit_builder = FakeOutfitBuilder(outfits=[Outfit(items=[item])])

    uc = BuildOutfit(user_repo, wardrobe_repo, weather_repo, outfit_builder)

    res = await uc.run(user_id=user.user_id, today=date.today())

    assert res.success is False
    assert res.message_key == ""  # как у тебя сейчас
    assert res.outfits is None
    assert res.weather is None
    assert res.style_used is None


@pytest.mark.asyncio
async def test_build_outfit_success_uses_city_override_and_style_used() \
        -> None:
    user = make_user()
    item = make_item(
        item_id=1,
        category=ClothingCategory.BOTTOM,
        subtype=ClothingSubtype.JEANS,
    )
    outfit = Outfit(items=[item])

    user_repo = FakeUserRepo(users=[user])
    wardrobe_repo = FakeWardrobeRepo(items=[item])

    override_city = "OtherCity"
    w = make_weather(date.today(), morning=10, day=12, evening=9,
                     city=override_city)
    weather_repo = FakeWeatherRepo({override_city: w})

    outfit_builder = FakeOutfitBuilder(outfits=[outfit])

    uc = BuildOutfit(user_repo, wardrobe_repo, weather_repo, outfit_builder)

    res = await uc.run(
        user_id=user.user_id,
        today=date.today(),
        city=override_city,
        style=Style.STREET,
        count_max=3,
    )

    assert res.success is True
    assert res.message_key == "success"

    assert res.weather is not None
    assert res.weather.city == override_city
    assert res.weather.temp_day == int(w.temperatures.day)

    assert res.outfits is not None
    assert len(res.outfits) == 1
    assert res.outfits[0].items[0].item_id == 1
    assert res.style_used == Style.STREET


@pytest.mark.asyncio
async def test_build_outfit_success_style_used_falls_back_to_user_favourite() \
        -> None:
    user = make_user()
    item = make_item(
        item_id=1,
        category=ClothingCategory.BOTTOM,
        subtype=ClothingSubtype.JEANS,
    )

    user_repo = FakeUserRepo(users=[user])
    wardrobe_repo = FakeWardrobeRepo(items=[item])
    weather_repo = FakeWeatherRepo({user.location: make_weather(date.today(),
                                                                morning=15,
                                                                day=22,
                                                                evening=16)})
    outfit_builder = FakeOutfitBuilder(outfits=[Outfit(items=[item])])

    uc = BuildOutfit(user_repo, wardrobe_repo, weather_repo, outfit_builder)

    res = await uc.run(user_id=user.user_id, today=date.today(), style=None)

    assert res.success is True
    assert res.message_key == "success"
    assert res.style_used == user.favourite_style
