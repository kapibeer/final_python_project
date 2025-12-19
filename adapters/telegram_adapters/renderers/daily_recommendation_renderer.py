import random
from typing import List, Optional

from domain import Outfit
from commands import DailyRecommendationResult
from .types import RenderMessage, RenderButton


class DailyRecommendationRenderer:
    """
    Рендерит daily recommendation:
    - погода (если есть)
    - пожелание дня (рандом)
    - take_with (если есть)
    - outfit (если есть)
    """

    WISHES: List[str] = [
        "Пусть день будет лёгким и удачным ✨",
        "Сегодня ты — главный герой 💅",
        "Пусть всё сложится ровно так, как тебе нужно 🌿",
        "Желаю спокойного темпа и хороших новостей ☀️",
        "Пусть люди будут добрыми, а дела — простыми 🤍",
        "Пусть будет время и на дела, и на себя 🫶",
        "Сегодня — день маленьких побед 🏆",
        "Пусть настроение держится крепко весь день 🌈",
    ]

    def render(self, result: DailyRecommendationResult) -> RenderMessage:
        # ошибки use-case
        if not result.success:
            return self._render_error(result.message_key)

        header = self._render_header(result)
        wish = self._render_wish()
        take_with = self._render_take_with(result)
        outfit_block = self._render_outfit_optional(result.outfit)

        parts = [p for p in [header, wish, take_with, outfit_block] if p]
        text = "\n\n".join(parts).strip()

        # если outfit нет
        if result.outfit is None:
            text += "\n\n" + (
                "Я не смог собрать лук из текущего гардероба 😔\n"
                "Добавь несколько вещей — и попробуем снова."
            )

        buttons = [
            [RenderButton("🧥 Гардероб", "wardrobe:open"),
             RenderButton("🏠 Меню", "menu:home")],
        ]

        # если outfit нет — логично дать кнопку добавить вещь
        if result.outfit is None:
            buttons = [
                [RenderButton("🏠 Меню", "menu:home")],
                [RenderButton("➕ Добавить вещь", "wardrobe:add")]
            ]

        return RenderMessage(text=text, buttons=buttons)

    # -------------------- helpers --------------------

    def _render_error(self, message_key: str) -> RenderMessage:
        if message_key == "not_found":
            return RenderMessage(
                text="Я не нашёл твой профиль 😶\n"
                "Давай зарегистрируемся заново.",
                buttons=[[RenderButton("✅ Начать", "user:start")]],
            )

        return RenderMessage(
            text="Что-то пошло не так 😔",
            buttons=[[RenderButton("🏠 Меню", "menu:home")]],
        )

    def _render_header(self, result: DailyRecommendationResult) -> str:
        w = result.weather
        st = result.style_used.value if result.style_used else "any"

        if not w:
            return f"Ежедневная рекомендация\nСтиль: {st}"

        icons: List[str] = []
        if getattr(w, "is_rain", False):
            icons.append("🌧")
        if getattr(w, "is_snow", False):
            icons.append("❄️")
        if getattr(w, "is_windy", False):
            icons.append("💨")
        icons_str = (" ".join(icons) + " ") if icons else ""

        city = getattr(w, "city", getattr(w, "location", ""))
        dt = getattr(w, "today", getattr(w, "date", None))
        date_str = dt.isoformat() if hasattr(dt, "isoformat") else ""

        t_m = getattr(w, "temp_morning", "")
        t_d = getattr(w, "temp_day", "")
        t_e = getattr(w, "temp_evening", "")

        return (
            f"{city} · {date_str}\n"
            f"{icons_str}🌡 {t_m}° утром · {t_d}° днём · {t_e}° вечером\n"
            f"Стиль: {st}"
        ).strip()

    def _render_wish(self) -> str:
        return f"**Пожелание дня:** {random.choice(self.WISHES)}"

    def _render_take_with(self, result: DailyRecommendationResult) -> str:
        tw = result.take_with
        if not tw or not getattr(tw, "items", None):
            return ""

        items = [str(x).strip() for x in tw.items if str(x).strip()]
        if not items:
            return ""

        lines = ["**Взять с собой:**"] + [f"• {x}" for x in items]
        return "\n".join(lines)

    def _render_outfit_optional(self, outfit: Optional[Outfit]) -> str:
        if outfit is None:
            return ""

        lines: List[str] = ["**Лук дня**"]
        for item in outfit.items:
            lines.append(
                f"• {item.category.value}: {item.subtype.value}"
                f" · {item.style.value} · {item.main_color.value}"
            )
        return "\n".join(lines)
