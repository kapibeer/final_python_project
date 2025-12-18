from typing import List
from domain import Outfit
from commands import BuildOutfitResult
from .types import RenderMessage, RenderButton


class OutfitBuildRenderer:
    """
    Рендерит один outfit из BuildOutfitResult по индексу.
    Индекс — 0-based.
    """

    def render(self, result: BuildOutfitResult, index: int) -> RenderMessage:
        # ошибки use-case
        if not result.success:
            return self._render_error(result.message_key)

        # пустой гардероб/не собралось
        if not result.outfits:
            return self._render_empty(result)

        total = len(result.outfits)
        idx = max(0, min(index, total - 1))
        outfit = result.outfits[idx]

        header = self._render_header(result)
        body = self._render_outfit(outfit, idx, total)
        text = f"{header}\n\n{body}".strip()

        # клавиатура
        if idx >= total - 1:
            buttons = [
                [RenderButton("🔁 Сгенерировать ещё",
                              self._regen_callback(result))],
                [RenderButton("🧥 Гардероб", "wardrobe:open"),
                 RenderButton("🏠 Меню", "menu:home")],
                [],
            ]
        else:
            buttons = [
                [
                    RenderButton("👍 Нравится", f"outfit:like:{idx}"),
                    RenderButton("👎 Не то", f"outfit:next:{idx + 1}"),
                ],
                [RenderButton("🧥 Гардероб", "wardrobe:open"),
                 RenderButton("🏠 Меню", "menu:home")],
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
        if message_key == "empty_wardrobe":
            return RenderMessage(
                text="У тебя пока нет вещей в гардеробе.\n"
                "Добавь несколько — и соберу лук 💅",
                buttons=[[RenderButton("🏠 Меню", "menu:home")],
                         [RenderButton("➕ Добавить вещь", "wardrobe:add")]],
            )
        return RenderMessage(
            text="Что-то пошло не так 😔",
            buttons=[[RenderButton("🏠 Меню", "menu:home")]],
        )

    def _render_empty(self, result: BuildOutfitResult) -> RenderMessage:
        # сюда попадём, если success=True, но outfits=None/[]
        return RenderMessage(
            text="Я не смог собрать лук из текущего гардероба 😔\n"
                 "Попробуй другой стиль или добавь вещи.",
            buttons=[
                [RenderButton("🔁 Сгенерировать ещё",
                              self._regen_callback(result))],
                [RenderButton("➕ Добавить вещь", "wardrobe:add")],
                [RenderButton("🏠 Меню", "menu:home")],
            ],
        )

    def _render_header(self, result: BuildOutfitResult) -> str:
        w = result.weather
        st = result.style_used.value if result.style_used else "any"

        if not w:
            return f"Стиль: {st}"

        icons: List[str] = []
        if getattr(w, "is_rain", False):
            icons.append("🌧")
        if getattr(w, "is_snow", False):
            icons.append("❄️")
        if getattr(w, "is_windy", False):
            icons.append("💨")
        icons_str = (" ".join(icons) + " ") if icons else ""

        # аккуратно, чтобы не зависеть от точных названий полей WeatherSummary
        location = getattr(w, "location", None) or getattr(w, "city", "")
        dt = getattr(w, "date", None) or getattr(w, "today", None)
        date_str = dt.isoformat() if hasattr(dt, "isoformat") else ""

        temps = getattr(w, "temperatures", None)
        if temps is not None:
            t_m = getattr(temps, "morning", getattr(w, "temp_morning", ""))
            t_d = getattr(temps, "day", getattr(w, "temp_day", ""))
            t_e = getattr(temps, "evening", getattr(w, "temp_evening", ""))
        else:
            t_m = getattr(w, "temp_morning", "")
            t_d = getattr(w, "temp_day", "")
            t_e = getattr(w, "temp_evening", "")

        return (
            f"{location} · {date_str}\n"
            f"{icons_str}🌡 {t_m}° утром · {t_d}° днём · {t_e}° вечером\n"
            f"Стиль: {st}"
        ).strip()

    def _render_outfit(self, outfit: Outfit, idx: int, total: int) -> str:
        lines: List[str] = [f"**Лук {idx + 1}/{total}**"]
        for item in outfit.items:
            lines.append(
                f"• {item.category.value}: {item.subtype.value}"
                f" · {item.style.value} · {item.main_color.value}"
            )
        return "\n".join(lines)

    def _regen_callback(self, result: BuildOutfitResult) -> str:
        style = result.style_used.value if result.style_used else "-"
        # если в WeatherSummary нет location/city — ок, будет "-"
        city = "-"
        if result.weather is not None:
            city = getattr(result.weather, "location", None) \
                or getattr(result.weather, "city", "-")
        return f"outfit:regen:{city}:{style}"
