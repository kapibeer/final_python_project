import random
from typing import List, Optional, ClassVar

from domain.models.outfit import Outfit
from commands.daily_recommendation import DailyRecommendationResult
from .types import RenderMessage, RenderButton
from dataclasses import dataclass


@dataclass(frozen=True)
class DailyRecommendationRenderer:
    """
    Рендерит daily recommendation:
    - погода (если есть)
    - пожелание дня (рандом)
    - take_with (если есть)
    - outfit (если есть)
    """

    WISHES: ClassVar[List[str]] = [
        "Пусть день будет лёгким и удачным ✨",
        "Сегодня ты — главный герой 💅",
        "Пусть всё сложится ровно так, как тебе нужно 🌿",
        "Желаю спокойного темпа и хороших новостей ☀️",
        "Пусть люди будут добрыми, а дела — простыми 🤍",
        "Пусть будет время и на дела, и на себя 🫶",
        "Сегодня — день маленьких побед 🏆",
        "Пусть настроение держится крепко весь день 🌈",
    ]

    TAKE_WITH_TEXT: ClassVar[dict[str, str]] = {
        "головной убор":
            "🧢 <b>Головной убор</b> — защитит от солнца и перегрева",

        "солнцезащитные очки":
            "🕶 <b>Солнцезащитные очки</b> — комфорт и стиль в одном флаконе",

        "SPF":
            "🧴 <b>SPF</b> — <i>обязателен</i> при активном солнце",

        "зонт":
            "☂️ <b>Зонт</b> — вдруг небо решит поплакать",

        "дождевик":
            "🌧 <b>Дождевик</b> — дождь не повод портить образ",

        "ветровка":
            "💨 <b>Ветровка</b> — спасёт от порывов ветра",

        "шапка":
            "⛄️ <b>Шапка</b> — чтобы было тепло и уютно",

        "шарф":
            "🧣 <b>Шарф</b> — защита для шеи",

        "перчатки/варежки":
            "🧤 <b>Перчатки или варежки</b> — руки скажут спасибо",

        "легкая непромокаемая куртка":
            "🧥 <b>Непромокаемая куртка</b> — <i>идеальна для влажной"
            " и сырой погоды</i>",

        "светоотражающие элементы":
            "✨ <b>Светоотражающие элементы</b> — сегодня туманно,"
            " так заметнее и безопаснее",

        "легкая куртка":
            "🧥 <b>Лёгкая куртка</b> — вечером станет прохладнее",

        "легкая кофта":
            "🧶 <b>Лёгкая кофта</b> — накинуть после заката",

        "куртка":
            "🧥 <b>Куртка</b> — пригодится ближе к вечеру",
            }

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
            return f"ЕЖЕДНЕВНАЯ РЕКОМЕНДАЦИЯ\nСтиль: {st}"

        icons: List[str] = []
        if getattr(w, "is_rain", False):
            icons.append("🌧")
        if getattr(w, "is_snow", False):
            icons.append("❄️")
        if getattr(w, "is_windy", False):
            icons.append("💨")
        icons_str = (" ".join(icons) + " ") if icons else ""

        city = w.city
        dt = w.required_date
        date_str = dt.isoformat() if hasattr(dt, "isoformat") else ""

        t_m = w.temp_morning
        t_d = w.temp_day
        t_e = w.temp_evening

        return (
            f"<i>{city} • {date_str.replace('-', '.')}</i>\n\n"
            f"<b>Осадки:</b> {icons_str}\n\n"
            f"<blockquote>"
            f"☀️ <b>Утро:</b> {t_m}°\n"
            f"⛅️ <b>День:</b> {t_d}°\n"
            f"🌙 <b>Вечер:</b> {t_e}°"
            f"</blockquote>\n\n"
            f"<b>Стиль:</b> {st}"
            )

    def _render_wish(self) -> str:
        return '<b>Пожелание на день:</b>\n' + \
                f'<i>{random.choice(self.WISHES)}</i>'

    def _render_take_with(self, result: DailyRecommendationResult) -> str:
        tw = result.take_with
        if not tw or not tw.items:
            return ""

        lines = ["<b>Что взять с собой 👜:</b>"]
        for key in tw.items:
            text = self.TAKE_WITH_TEXT.get(key, f"• {key}")
            lines.append(f"• {text}")

        return "\n".join(lines)

    def _render_outfit_optional(self, outfit: Optional[Outfit]) -> str:
        if outfit is None:
            return ""

        lines: List[str] = ["<blockquote>Aутфит для тебя!💋 </blockquote>\n"]
        for item in outfit.items:
            lines.append(
                f"•<b>{item.name}:</b> "
                f"{item.style.value} · {item.main_color.value}"
            )
        return "\n".join(lines)
