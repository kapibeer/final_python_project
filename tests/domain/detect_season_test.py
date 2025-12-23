import pytest
from datetime import date

from domain.models.season import Season

from domain.services.detect_season import detect_season

from tests.helpers import make_weather


@pytest.mark.parametrize(
    "d, expected",
    [
        (date(2025, 3, 1), Season.SPRING),
        (date(2025, 6, 1), Season.SUMMER),
        (date(2025, 9, 1), Season.AUTUMN),
        (date(2025, 12, 1), Season.WINTER),
    ],
)
def test_detect_season_returns_season_on_exact_start_day(d: date,
                                                         expected: Season):
    w = make_weather(d, morning=0, day=0, evening=0)
    assert detect_season(w) == expected


def test_detect_season_spring_within_21_days_and_signs_returns_spring() \
        -> None:
    # 21 день до 1 марта 2025 -> 8 февраля 2025
    d = date(2025, 2, 8)
    # SPRING signs:
    # 1) day >= 0
    # 2) not snow
    # 3) rain or sleet
    # 4) day - morning >= 5
    # 5) sunny and day >= 5
    # сделаем (1) + (3) + (4)
    w = make_weather(
        d,
        morning=-5,
        day=2,
        evening=0,
        is_rain=True,
        is_snow=False,
    )
    assert detect_season(w) == Season.SPRING


def test_detect_season_winter_within_21_days_and_signs_returns_winter() \
        -> None:
    # 21 день до 1 декабря 2025 -> 10 ноября 2025
    d = date(2025, 11, 10)
    # WINTER signs:
    # 1) day < 5
    # 2) snow or sleet
    # 3) morning < 0
    # 4) windy and day < 10
    # 5) not rain and day < 8
    # сделаем (1) + (3) + (2)
    w = make_weather(
        d,
        morning=-2,
        day=3,
        evening=0,
        is_snow=True,
        is_rain=False,
    )
    assert detect_season(w) == Season.WINTER


def test_detect_season_outside_window_returns_none_even_if_signs_match() \
        -> None:
    # далеко от 1 марта — даже при весенних признаках должно быть None
    d = date(2025, 1, 1)
    w = make_weather(
        d,
        morning=-5,
        day=2,
        evening=0,
        is_rain=True,
        is_snow=False,
        is_sunny=True,
    )
    assert detect_season(w) is None


def test_detect_season_start_day_has_priority_over_signs() -> None:
    # 1 марта — должен вернуться SPRING даже если выставили другие признаки
    d = date(2025, 3, 1)
    w = make_weather(
        d,
        morning=-10,
        day=-3,
        evening=-5,
        is_snow=True,
        is_windy=True,
        is_cloudy=True,
    )
    assert detect_season(w) == Season.SPRING
