import pytest
from datetime import date

from domain.services.weather_classifier import classify_weather

from tests.helpers import make_weather


@pytest.mark.parametrize(
    "temps, expected",
    [
        ((-10, -8, -6), 4),   # very cold
        ((-5, -5, -5), 4),   # boundary very cold
        ((0, 5, 10), 3),     # cold
        ((10, 10, 10), 3),   # boundary cold
        ((11, 15, 20), 2),   # mild
        ((20, 20, 20), 2),   # boundary mild
        ((21, 25, 30), 1),   # hot
    ]
)
def test_classify_weather_levels(temps, expected):  # type: ignore
    weather = make_weather(d=date(2025, 1, 1),
                           morning=temps[0],  # type: ignore
                           day=temps[1], evening=temps[2])  # type: ignore
    result = classify_weather(weather)  # type: ignore
    assert result == expected
