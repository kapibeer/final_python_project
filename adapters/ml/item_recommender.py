from typing import List, Optional, Dict, Tuple
from domain import User, WeatherSnap
from domain import ClothingItem, Style, TopGroup, \
    ClothingCategory, WarmthLevel
from domain.services.item_recommender import ItemRecommender
from domain.services.weather_classifier import classify_weather
import joblib
import pandas as pd

clf = joblib.load("/Users/kapitolinakondakova/PYTHON_FINAL_PROJECT/"
                  "ml/items_recommender.pkl")


SIMILAR_STYLES: dict[Style, set[Style]] = {
    Style.OFFICIAL: {Style.CASUAL},
    Style.CASUAL: {Style.OFFICIAL, Style.STREET, Style.SPORT},
    Style.SPORT: {Style.CASUAL, Style.STREET, Style.OUTDOOR},
    Style.PARTY: {Style.CASUAL, Style.OFFICIAL, Style.STREET},
    Style.STREET: {Style.CASUAL, Style.SPORT},
    Style.OUTDOOR: {Style.CASUAL, Style.SPORT, Style.STREET},
}

TOP_WARMTH_RULES: Dict[Optional[TopGroup], Dict[int, int]] = {
    TopGroup.BASE_TOPS: {
        4: 1,
        3: 1,
        2: 1,
        1: 1,
    },
    TopGroup.FINAL_LAYER_TOPS: {
        4: 2,
        3: 2,
        2: 2,
        1: 1,
    },
    TopGroup.LAYERED_TOPS: {
        4: 2,
        3: 2,
        2: 2,
        1: 1,
    },
    TopGroup.TRANSFORMABLE_TOPS: {
        4: 2,
        3: 2,
        2: 2,
        1: 1,
    },
    TopGroup.ONEPIECE_CLOTH: {
        4: 2,
        3: 2,
        2: 2,
        1: 1,
    },

    None: {
        4: 2,
        3: 2,
        2: 2,
        1: 1,
    },
}

items_warmth_level_to_num = {
    WarmthLevel.LIGHT: 1,
    WarmthLevel.MEDIUM: 2,
    WarmthLevel.WARM: 3,
    WarmthLevel.VERY_WARM: 4,
}


class MLItemRecommender(ItemRecommender):
    def recommend(
        self,
        user: User,
        wardrobe: List[ClothingItem],
        weather: WeatherSnap,
        style: Optional[Style] = None,
    ) -> List[Tuple[ClothingItem, float]]:

        weather_coldness: int = classify_weather(weather)

        effective_style: Style = style or user.favourite_style

        df = self.build_features_df(
            user=user,
            wardrobe=wardrobe,
            weather=weather,
            weather_coldness=weather_coldness,
            style=effective_style,
        )
        probs = clf.predict_proba(df)[:, 1]

        scored_items: List[Tuple[ClothingItem, float]] = list(
            zip(wardrobe, probs)
        )
        if effective_style is not None:
            scored_items = self._apply_style_boost(scored_items, style)
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return scored_items

    def weather_coldness_for_item(self, item: ClothingItem,
                                  weather_coldness: int) -> int:
        if item.category == ClothingCategory.OUTERWEAR:
            return weather_coldness
        if item.category == ClothingCategory.TOP:
            return TOP_WARMTH_RULES[item.top_group][weather_coldness]
        return max(1, weather_coldness - 1)

    def build_features_df(
        self,
        user: User,
        wardrobe: List[ClothingItem],
        weather: WeatherSnap,
        weather_coldness: int,
        style: Style,      # уже не Optional
    ) -> pd.DataFrame:
        rows = [
            self.item_to_features(
                user=user,
                weather=weather,
                item=item,
                weather_coldness=weather_coldness,
                style=style,
            )
            for item in wardrobe
        ]
        return pd.DataFrame(rows)

    def item_to_features(
        self,
        user: User,
        weather: WeatherSnap,
        item: ClothingItem,
        weather_coldness: int,
        style: Style,
    ) -> dict:
        user_style_str = style.value

        return {
            "cold_sensitivity": user.cold_sensitivity.value,
            "user_style": user_style_str,
            "item_type": item.category.value,
            "item_subtype": item.subtype.value,
            "item_style": item.style.value,
            "item_color": item.main_color.value,
            "item_warmth": items_warmth_level_to_num[item.warmth_level],
            "is_waterproof": int(item.is_waterproof),
            "is_windproof": int(item.is_windproof),
            "weather_coldness": self.weather_coldness_for_item(
                item, weather_coldness
            ),
            "is_rain": int(
                weather.is_rain
                and item.category == ClothingCategory.OUTERWEAR
            ),
            "is_snow": int(
                weather.is_snow
                and item.category == ClothingCategory.OUTERWEAR
            ),
            "is_windy": int(
                weather.is_windy
                and item.category == ClothingCategory.OUTERWEAR
            ),
        }

    def _apply_style_boost(
        self,
        scored_items: List[Tuple[ClothingItem, float]],
        target_style: Style,
    ) -> List[Tuple[ClothingItem, float]]:
        """
        Чуть подкручиваем скоры модели, чтобы сильнее
        учитывать желаемый стиль пользователя.
        """
        similar = SIMILAR_STYLES.get(target_style, set())

        boosted: List[Tuple[ClothingItem, float]] = []
        for item, base_p in scored_items:
            boost = 0.0
            if item.style == target_style:
                boost = 0.2
            elif item.style in similar:
                boost = 0.10
            else:
                boost = -0.15

            new_p = max(0.0, min(1.0, base_p + boost))
            boosted.append((item, new_p))

        return boosted
