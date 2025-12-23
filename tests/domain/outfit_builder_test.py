import pytest
from datetime import date

from tests.helpers import make_weather, make_item, make_user

from domain.models.user import ColdSensitivity
from domain.models.clothing_item import (
    ClothingCategory,
    ClothingSubtype,
    WarmthLevel,
)

from domain.models.outfit import Outfit

from domain.services.outfit_builder import OutfitBuilder


# ---------- helpers for tests ----------

class FakeRecommender:
    """Заглушка ML-рекомендера: возвращает всем вещам фиксированный скор."""
    def recommend(self, user, wardrobe, weather, style=None):  # type: ignore
        return [(item, 0.5) for item in wardrobe]  # type: ignore


# ---------- tests (самые необходимые) ----------

def test_effective_coldness_applies_user_sensitivity_shift():
    b = OutfitBuilder(FakeRecommender())

    # погодная холодность 3 (cold)
    base = 3

    u_low = make_user(ColdSensitivity.LOW)
    u_med = make_user(ColdSensitivity.MEDIUM)
    u_high = make_user(ColdSensitivity.HIGH)

    assert b._effective_coldness(base, u_low) == 2  # type: ignore
    assert b._effective_coldness(base, u_med) == 3  # type: ignore
    assert b._effective_coldness(base, u_high) == 4  # type: ignore


def test_shorts_penalty_is_zero_in_hot_weather():
    b = OutfitBuilder(FakeRecommender())

    shorts = make_item(
        item_id=1,
        category=ClothingCategory.BOTTOM,
        subtype=ClothingSubtype.SHORTS,
    )

    assert b._shorts_in_cold_penalty(1, shorts) == 0.0  # type: ignore


@pytest.mark.parametrize("coldness", [2, 3, 4])
def test_shorts_penalty_positive_in_non_hot_weather(coldness: int):
    b = OutfitBuilder(FakeRecommender())

    shorts = make_item(
        item_id=1,
        category=ClothingCategory.BOTTOM,
        subtype=ClothingSubtype.SHORTS,
    )

    assert b._shorts_in_cold_penalty(coldness, shorts) > 0.0  # type: ignore


def test_outerwear_weather_penalty_requires_waterproof_when_precipitation():
    b = OutfitBuilder(FakeRecommender())

    weather = make_weather(
        date(2025, 1, 10),
        morning=1, day=3, evening=0,
        is_rain=True,
    )

    coat_not_waterproof = make_item(
        item_id=1,
        category=ClothingCategory.OUTERWEAR,
        subtype=ClothingSubtype.COAT,
        is_waterproof=False,
    )
    coat_waterproof = make_item(
        item_id=2,
        category=ClothingCategory.OUTERWEAR,
        subtype=ClothingSubtype.COAT,
        is_waterproof=True,
    )

    assert b._outerwear_weather_penalty(weather,  # type: ignore
                                        coat_not_waterproof) == 1.0
    assert b._outerwear_weather_penalty(weather,  # type: ignore
                                        coat_waterproof) == 0.0


def test_outerwear_weather_penalty_wind_requires_windproof():
    b = OutfitBuilder(FakeRecommender())

    weather = make_weather(
        date(2025, 1, 10),
        morning=1, day=3, evening=0,
        is_rain=True,
        is_windy=True,
    )

    jacket_ok = make_item(
        item_id=1,
        category=ClothingCategory.OUTERWEAR,
        subtype=ClothingSubtype.JACKET,
        is_waterproof=True,
        is_windproof=True,
    )
    jacket_no_wind = make_item(
        item_id=2,
        category=ClothingCategory.OUTERWEAR,
        subtype=ClothingSubtype.JACKET,
        is_waterproof=True,
        is_windproof=False,
    )

    assert b._outerwear_weather_penalty(weather,  # type: ignore
                                        jacket_ok) == 0.0
    assert b._outerwear_weather_penalty(weather,  # type: ignore
                                        jacket_no_wind) == 0.5


def test_outerwear_warmth_penalty_under_is_stronger_than_over():
    b = OutfitBuilder(FakeRecommender())

    # coldness=4 -> target=VERY_WARM(4)
    weather_coldness = 4

    too_light = make_item(
        item_id=1,
        category=ClothingCategory.OUTERWEAR,
        subtype=ClothingSubtype.COAT,
        warmth=WarmthLevel.MEDIUM,   # 2 (недобор на 2)
    )
    too_warm = make_item(
        item_id=2,
        category=ClothingCategory.OUTERWEAR,
        subtype=ClothingSubtype.COAT,
        warmth=WarmthLevel.VERY_WARM,  # 4 (в норму)
    )
    # делаем "перебор" на 1 шаг относительно mild
    mild_target = 2
    over_for_mild = make_item(
        item_id=3,
        category=ClothingCategory.OUTERWEAR,
        subtype=ClothingSubtype.COAT,
        warmth=WarmthLevel.WARM,  # 3 (перебор на 1)
    )

    p_under = b._outerwear_warmth_penalty(weather_coldness,  # type: ignore
                                          too_light)
    p_ok = b._outerwear_warmth_penalty(weather_coldness,  # type: ignore
                                       too_warm)
    p_over = b._outerwear_warmth_penalty(mild_target,  # type: ignore
                                         over_for_mild)

    assert p_ok == 0.0
    assert p_under > p_over  # недобор сильнее штрафуется, чем перебор


def test_score_outfit_increases_penalty_for_shorts_in_cold():
    """
    Минимальная проверка, что штраф за шорты реально влияет на итоговый скор.
    (без фиксации рандома и без build())
    """
    b = OutfitBuilder(FakeRecommender())
    user = make_user(ColdSensitivity.MEDIUM)

    cold_weather = make_weather(
        date(2025, 1, 10),
        morning=0, day=5, evening=1,
        is_rain=False,
    )

    item_scores = {1: 0.5, 2: 0.5}

    with_shorts = Outfit(items=[
        make_item(item_id=1, category=ClothingCategory.BOTTOM,
                  subtype=ClothingSubtype.SHORTS),
    ])
    with_jeans = Outfit(items=[
        make_item(item_id=2, category=ClothingCategory.BOTTOM,
                  subtype=ClothingSubtype.JEANS),
    ])

    s_shorts = b._score_outfit(  # type: ignore
        outfit=with_shorts,
        user=user,
        weather_coldness=3,
        weather=cold_weather,
        item_scores=item_scores,
    )
    s_jeans = b._score_outfit(  # type: ignore
        outfit=with_jeans,
        user=user,
        weather_coldness=3,
        weather=cold_weather,
        item_scores=item_scores,
    )

    assert s_jeans > s_shorts
