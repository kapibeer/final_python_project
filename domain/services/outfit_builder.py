from typing import List, Optional, Tuple, Dict, Any
from domain.models.outfit import Outfit
from domain.models.weather_snap import WeatherSnap
from domain.models.user import User
from domain.models.clothing_item import WarmthLevel
from domain.models.clothing_item import ClothingItem, Style, \
    Color, ClothingCategory, TopGroup
from domain.services.item_recommender import ItemRecommender
from domain.services.weather_classifier import classify_weather
from collections import Counter, defaultdict
from dataclasses import dataclass
import random

COLOR_GROUP: dict[Color, str] = {
    # базовые нейтральные
    Color.BLACK:  "neutral",
    Color.WHITE:  "neutral",
    Color.GREY:   "neutral",
    Color.BEIGE:  "neutral",
    Color.BROWN:  "neutral",
    Color.KHAKI:  "neutral",

    # мягкие холодные
    Color.NAVY:   "soft",
    Color.BLUE:   "soft",
    Color.GREEN:  "soft",

    # яркие, заметные акценты
    Color.RED:    "bright",
    Color.YELLOW: "bright",
    Color.ORANGE: "bright",
    Color.PINK:   "bright",
    Color.PURPLE: "bright",

    # особый случай
    Color.MULTICOLOR: "multicolor"
}


def color_harmony_score(items: List[ClothingItem]) -> float:
    """
    Грубая оценка цветовой гармонии аутфита.
    Чем выше score, тем более согласованными считаются цвета.
    """
    if not items:
        return 0.0

    groups = [COLOR_GROUP.get(i.main_color, "neutral") for i in items]
    c = Counter(groups)

    n_neutral = c["neutral"]
    n_soft = c["soft"]
    n_bright = c["bright"]
    n_multi = c["multicolor"]

    score = 0.0

    score += 0.3 * min(n_neutral, 3)

    if n_bright == 0:
        score += 0.2
    elif n_bright == 1:
        score += 0.8
    elif n_bright == 2:
        score += 0.2
    else:
        score -= 0.8

    if n_soft > 0:
        score += 0.2 * min(n_soft, 2)
        if n_neutral == 0 and n_bright >= 2:
            score -= 0.3

    if n_multi == 1:
        if n_bright >= 2:
            score -= 1.0
    elif n_multi >= 2:
        score -= 1.0

    distinct_groups = len([g for g, cnt in c.items() if cnt > 0])
    if distinct_groups >= 4:
        score -= 0.5

    MAX_COLOR_SCORE = 2.0
    score = score / MAX_COLOR_SCORE

    score = max(-1.0, min(1.0, score))

    return score


@dataclass
class Slot:
    category: ClothingCategory
    top_group: Optional[TopGroup] = None


@dataclass
class Template:
    slots: List[Slot]


WEATHER_TEMPLATES: dict[int, list[Template]] = {

    # 1 — HOT WEATHER
    1: [
        Template(slots=[
            Slot(category=ClothingCategory.TOP, top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP, top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.ONEPIECE_CLOTH),
        ]),
    ],

    # 2 — MILD WEATHER
    2: [
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.TRANSFORMABLE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.LAYERED_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.TRANSFORMABLE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.FINAL_LAYER_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.ONEPIECE_CLOTH),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.TRANSFORMABLE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.LAYERED_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.TRANSFORMABLE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.FINAL_LAYER_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ])
    ],

    # 3 — COLD WEATHER
    3: [
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.ONEPIECE_CLOTH),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.TRANSFORMABLE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.LAYERED_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.TRANSFORMABLE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.FINAL_LAYER_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ])
    ],

    # 4 — VERY COLD WEATHER
    4: [
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.TRANSFORMABLE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.BASE_TOPS),
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.LAYERED_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.TRANSFORMABLE_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ]),
        Template(slots=[
            Slot(category=ClothingCategory.TOP,
                 top_group=TopGroup.FINAL_LAYER_TOPS),
            Slot(category=ClothingCategory.BOTTOM),
            Slot(category=ClothingCategory.OUTERWEAR),
        ])
    ],
}


WARMTH_VALUE: dict[WarmthLevel, int] = {
    WarmthLevel.LIGHT: 1,
    WarmthLevel.MEDIUM: 2,
    WarmthLevel.WARM: 3,
    WarmthLevel.VERY_WARM: 4,
}


# какая “норма” по теплоте outerwear для каждой холодности
OUTERWEAR_TARGET_WARMTH: dict[int, int] = {
    1: 1,  # HOT -> максимум легкое
    2: 2,  # MILD -> medium
    3: 3,  # COLD -> warm
    4: 4,  # VERY COLD -> very_warm
}


class OutfitBuilder:
    """
    Доменный сервис: собирает аутфиты по шаблонам,
    используя ML-рекомендер для скоринга отдельных вещей.
    """

    def __init__(self, recommender: ItemRecommender):
        self._recommender = recommender

    def build(
        self,
        user: User,
        wardrobe: List[ClothingItem],
        weather: WeatherSnap,
        style: Optional[Style] = None,
        count_max: int = 1,
    ) -> List[Outfit]:
        if not wardrobe:
            return []

        # Скорим все вещи из гардероба
        scored_items: List[Tuple[ClothingItem, float]] = (
            self._recommender.recommend(
                user=user,
                wardrobe=wardrobe,
                weather=weather,
                style=style,
            )
        )
        if not scored_items:
            return []

        item_scores: Dict[int, float] = {
            item.item_id: score for item, score in scored_items
        }
        # Группируем по (категори, топ груп)
        grouped = self._group_items(scored_items)

        # Выбираем набор шаблонов под текущую "холодность" погоды
        weather_coldness = classify_weather(weather)
        templates = WEATHER_TEMPLATES.get(weather_coldness, [])
        if not templates:
            return []

        # Генерируем много кандидатов-аутфитов с рандомом
        candidates: List[Outfit] = []
        seen_signatures: set[tuple[Any]] = set()

        max_outfits = max(1, count_max)
        max_attempts = max_outfits * 10
        target_candidates = max_outfits * 3

        attempts = 0
        while len(candidates) < target_candidates and attempts < max_attempts:
            attempts += 1

            template = random.choice(templates)  # рандом по шаблонам
            items_for_outfit: List[ClothingItem] = []

            # пытаемся подобрать вещи под каждый слот шаблона
            for slot in template.slots:
                key = (slot.category, slot.top_group)
                slot_candidates = grouped.get(key, [])
                if not slot_candidates:
                    items_for_outfit = []
                    break

                chosen = self._choose_for_slot(
                    slot_candidates,
                    already_used=items_for_outfit,
                    top_n=5,
                )
                if chosen is None:
                    items_for_outfit = []
                    break

                items_for_outfit.append(chosen)

            if not items_for_outfit:
                continue

            # проверяем, что не было такого еще
            signature: tuple[Any] = \
                tuple(sorted(i.item_id for i in items_for_outfit))
            if signature in seen_signatures:
                continue

            seen_signatures.add(signature)
            candidates.append(Outfit(items=items_for_outfit))

        if not candidates:
            return []

        # Оцениваем аутфиты:
        # средний ML-скор по вещам + бонус за цветовую гармонию
        scored_outfits: List[Tuple[Outfit, float]] = []
        for outfit in candidates:
            score = self._score_outfit(outfit=outfit, item_scores=item_scores,
                                       weather_coldness=weather_coldness)
            scored_outfits.append((outfit, score))

        scored_outfits.sort(key=lambda x: x[1], reverse=True)

        # 6. Возвращаем top-k аутфитов
        best_outfits = [o for (o, _) in scored_outfits[:max_outfits]]
        return best_outfits

    def _group_items(
        self,
        scored_items: List[Tuple[ClothingItem, float]],
    ) -> Dict[Tuple[ClothingCategory, Optional[TopGroup]],
              List[Tuple[ClothingItem, float]]]:
        """
        Группируем вещи по (category, top_group),
        сортируем внутри группы по скору по убыванию.
        """
        grouped: Dict[
            Tuple[ClothingCategory, Optional[TopGroup]],
            List[Tuple[ClothingItem, float]]
        ] = defaultdict(list)

        for item, score in scored_items:
            top_group = getattr(item, "top_group", None)
            key = (item.category, top_group)
            grouped[key].append((item, score))

        for key in grouped:
            grouped[key].sort(key=lambda x: x[1], reverse=True)

        return grouped

    def _choose_for_slot(
        self,
        candidates: List[Tuple[ClothingItem, float]],
        already_used: List[ClothingItem],
        top_n: int = 5,
    ) -> Optional[ClothingItem]:
        """
        Выбираем вещь для слота:
        - не берём то, что уже в этом аутфите;
        - случайный выбор из top-N по скору
        """
        used_ids = {i.item_id for i in already_used}
        filtered = [(item, score) for (item, score) in candidates
                    if item.item_id not in used_ids]
        if not filtered:
            return None

        subset = filtered[:top_n]
        scores = [s for _, s in subset]

        # приоритет лучшим вещам — с большим весом
        alpha = 3.0
        weights = [pow(2.71828, alpha * s) for s in scores]
        total = sum(weights)
        if total <= 0:
            return random.choice([item for (item, _) in subset])

        probs = [w / total for w in weights]
        chosen_item, _ = random.choices(subset, weights=probs, k=1)[0]
        return chosen_item

    def _score_outfit(
        self,
        outfit: Outfit,
        weather_coldness: int,
        item_scores: Dict[int, float],
        lambda_color: float = 0.5,
        lambda_outerwear: float = 0.2
    ) -> float:
        """
        Итоговый скор аутфита:
        - средний ML-скор по вещам
        - плюс бонус (или штраф) за цветовую гармонию.
        """
        if not outfit.items:
            return -1e9

        ml_scores = [item_scores.get(i.item_id, 0.0) for i in outfit.items]
        base_ml = sum(ml_scores) / len(ml_scores)

        outerwear_penalty = 0.0
        for it in outfit.items:
            outerwear_penalty += \
                self._outerwear_warmth_penalty(weather_coldness, it)

        color_score = color_harmony_score(outfit.items)

        return base_ml + lambda_color * color_score \
            - lambda_outerwear * outerwear_penalty

    def _outerwear_warmth_penalty(self, weather_coldness: int,
                                  item: ClothingItem) -> float:
        if item.category != ClothingCategory.OUTERWEAR:
            return 0.0

        target = OUTERWEAR_TARGET_WARMTH.get(weather_coldness, 2)
        actual = WARMTH_VALUE.get(item.warmth_level, 2)

        diff = actual - target
        penalty_per_step = 0.35
        return penalty_per_step * abs(diff)
