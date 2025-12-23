from datetime import date

from domain.services.take_with_builder import TakeWithBuilder
from tests.helpers import make_weather


def test_get_season_mapping():
    b = TakeWithBuilder()
    assert b._get_season(date(2025, 1, 10)) == "winter"  # type: ignore
    assert b._get_season(date(2025, 4, 10)) == "spring"  # type: ignore
    assert b._get_season(date(2025, 7, 10)) == "summer"  # type: ignore
    assert b._get_season(date(2025, 10, 10)) == "autumn"  # type: ignore


def test_sunny_hot_adds_hat_glasses_and_spf_when_uv_high():
    b = TakeWithBuilder()
    w = make_weather(d=date(2025, 7, 10),
                     morning=18, day=25, evening=20,
                     is_sunny=True,
                     is_uv_high=True)
    rec = b.build(w)
    assert "головной убор" in rec.items
    assert "солнцезащитные очки" in rec.items
    assert "SPF" in rec.items


def test_precipitation_storm_adds_raincoat_only_and_returns_early():
    b = TakeWithBuilder()
    w = make_weather(d=date(2025, 6, 10),
                     morning=15, day=18, evening=14,
                     is_storm=True,
                     is_rain=True)
    rec = b.build(w)
    assert "дождевик" in rec.items
    assert "зонт" not in rec.items


def test_rain_adds_umbrella():
    b = TakeWithBuilder()
    w = make_weather(
        d=date(2025, 9, 10),
        morning=12, day=16, evening=11,
        is_rain=True,
    )
    rec = b.build(w)
    assert "зонт" in rec.items


def test_wind_adds_windbreaker():
    b = TakeWithBuilder()
    w = make_weather(
        d=date(2025, 9, 10),
        morning=12, day=16, evening=11,
        is_windy=True,
    )
    rec = b.build(w)
    assert "ветровка" in rec.items


def test_cold_adds_hat_scarf_gloves():
    b = TakeWithBuilder()
    w = make_weather(
        d=date(2025, 12, 10),
        morning=0, day=6, evening=-1,
    )
    rec = b.build(w)
    assert "шапка" in rec.items
    assert "шарф" in rec.items
    assert "перчатки/варежки" in rec.items


def test_humid_and_cool_adds_light_waterproof_jacket():
    b = TakeWithBuilder()
    w = make_weather(
        d=date(2025, 10, 10),
        morning=10, day=18, evening=11,
        is_humid=True,
    )
    rec = b.build(w)
    assert "легкая непромокаемая куртка" in rec.items


def test_fog_adds_reflective_elements():
    b = TakeWithBuilder()
    w = make_weather(
        d=date(2025, 10, 10),
        morning=10, day=12, evening=9,
        is_fog=True,
    )
    rec = b.build(w)
    assert "светоотражающие элементы" in rec.items


def test_evening_cooling_spring_adds_light_jacket_when_big_drop():
    b = TakeWithBuilder()
    w = make_weather(
        d=date(2025, 4, 10),  # spring
        morning=8, day=16, evening=10,
    )
    rec = b.build(w)
    assert "легкая куртка" in rec.items


def test_evening_cooling_skipped_if_already_has_waterproof_stuff():
    b = TakeWithBuilder()
    w = make_weather(
        d=date(2025, 10, 10),
        morning=10, day=18, evening=8,
        is_humid=True,
        is_windy=False,
    )
    rec = b.build(w)
    # ранний return в evening_cooling должен сработать
    assert "легкая непромокаемая куртка" in rec.items
    assert "куртка" not in rec.items
    assert "легкая куртка" not in rec.items
    assert "легкая кофта" not in rec.items
