import pytest
from datetime import date

from commands.season_mailing import SeasonMailing
from domain.models.season import Season
from tests.helpers import make_weather, make_user, FakeUserRepo, \
    FakeWeatherRepo

pytestmark = pytest.mark.asyncio


async def test_no_users_returns_empty():
    user_repo = FakeUserRepo(users=[])
    weather_repo = FakeWeatherRepo(weather_by_city={})

    usecase = SeasonMailing(user_repo, weather_repo)
    result = await usecase.run()

    assert result == []


async def test_user_without_weather_skipped():
    user = make_user()
    user.location = "Nowhere"

    user_repo = FakeUserRepo(users=[user])
    weather_repo = FakeWeatherRepo(weather_by_city={})

    usecase = SeasonMailing(user_repo, weather_repo)
    result = await usecase.run()

    assert result == []
    assert user_repo.updated == []


async def test_no_season_detected():
    user = make_user()
    weather = make_weather(
        date.today(),
        morning=10, day=10, evening=10,
        is_rain=False, is_snow=False
    )

    user_repo = FakeUserRepo(users=[user])
    weather_repo = FakeWeatherRepo({user.location: weather})

    usecase = SeasonMailing(user_repo, weather_repo)
    result = await usecase.run()

    assert result == []
    assert user_repo.updated == []


async def test_season_detected_and_user_notified():
    user = make_user()
    d = date(2025, 3, 1)

    weather = make_weather(
        d,
        morning=0, day=5, evening=0,
        is_rain=True,
    )

    user_repo = FakeUserRepo(users=[user])
    weather_repo = FakeWeatherRepo({user.location: weather})

    usecase = SeasonMailing(user_repo, weather_repo)
    result = await usecase.run()

    assert len(result) == 1
    assert result[0].user_id == user.user_id
    assert result[0].season is not None
    assert user.last_season_notifiied == result[0].season
    assert len(user_repo.updated) == 1


async def test_same_season_not_sent_twice():
    user = make_user()
    user.last_season_notifiied = Season.SPRING

    weather = make_weather(
        date.today(),
        morning=5, day=10, evening=5,
        is_rain=True,
    )

    user_repo = FakeUserRepo(users=[user])
    weather_repo = FakeWeatherRepo({user.location: weather})

    usecase = SeasonMailing(user_repo, weather_repo)
    result = await usecase.run()

    assert result == []
    assert user_repo.updated == []
