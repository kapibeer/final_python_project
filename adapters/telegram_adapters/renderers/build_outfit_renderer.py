from typing import List

from commands import BuildOutfitResult
from domain import Outfit
from .types import RenderMessage, RenderButton


class BuildOutfitRenderer:
    """
    Renderer для результата BuildOutfit.
    Никакой доменной логики — только форматирование.
    """

    def render(self, result: BuildOutfitResult) -> RenderMessage:
        if not result.success:
            return self._render_error(result.message_key)

        # На всякий случай
        if not result.outfits:
            return RenderMessage(
                text="Я не смог собрать лук из текущего гардероба 😔\n"
                     "Попробуй другой стиль или добавь вещи.",
                buttons=[
                    [RenderButton("➕ Добавить вещь", "wardrobe:add")],
                    [RenderButton("🎛 Настройки", "prefs:open")],
                ],
            )

        header = self._render_weather_header(result)
        outfits_text = self._render_outfits(result.outfits)

        text = header + "\n\n" + outfits_text

        buttons = [
            [
                RenderButton("🔁 Ещё варианты", self._retry_callback(result)),
                RenderButton("🎛 Стиль", "prefs:style"),
            ],
            [
                RenderButton("🧥 Гардероб", "wardrobe:open"),
                RenderButton("🏠 Меню", "menu:home"),
            ],
        ]

        return RenderMessage(text=text, buttons=buttons)

    def _render_error(self, message_key: str) -> RenderMessage:
        if message_key == "not_found":
            return RenderMessage(
                text="Я не нашёл твоего профиля"
                "😶\nДавай зарегистрируемся заново.",
                buttons=[[RenderButton("✅ Начать", "user:start")]],
            )
        if message_key == "empty_wardrobe":
            return RenderMessage(
                text="У тебя пока нет вещей в гардеробе.\nДобавь хотя бы пару"
                "— и соберу лук 💅",
                buttons=[[RenderButton("➕ Добавить вещь", "wardrobe:add")]],
            )

        return RenderMessage(
            text="Что-то пошло не так 😔",
            buttons=[[RenderButton("🏠 Меню", "menu:home")]],
        )

    def _render_weather_header(self, result: BuildOutfitResult) -> str:
        w = result.weather
        style = result.style_used.value if result.style_used else "any"

        # Иконки
        icons: List[str] = []
        if w and w.is_rain:
            icons.append("🌧")
        if w and w.is_snow:
            icons.append("❄️")
        if w and w.is_windy:
            icons.append("💨")

        icons_str = (" ".join(icons) + " ") if icons else ""

        # coldness_level 1..4 можно маппить в слова
        coldness_label = ""
        if w:
            coldness_label = {1: "hot", 2: "mild", 3: "cold",
                              4: "very_cold"}.get(w.coldness_level, "")

        if not w:
            return f"Стиль: {style}"

        return (
            f"{w.city} · {w.date.isoformat()}\n"
            f"{icons_str}🌡 {w.temp_morning}° "
            "утром · {w.temp_day}° днём · {w.temp_evening}° вечером\n"
            f"Погода: {coldness_label}\n"
            f"Стиль: {style}"
        )

    def _render_outfits(self, outfits: List[Outfit]) -> str:
        lines: List[str] = []
        for idx, outfit in enumerate(outfits, 1):
            lines.append(f"**Лук #{idx}**")
            for item in outfit.items:
                # можно сделать красивее: эмодзи по категории
                cat = item.category.value
                subtype = item.subtype.value
                color = item.main_color.value
                st = item.style.value
                lines.append(f"• {cat}: {subtype} · {st} · {color}")
            lines.append("")  # пустая строка между луками
        return "\n".join(lines).strip()

    def _retry_callback(self, result: BuildOutfitResult) -> str:
        """
        callback_data обычно должен быть коротким.
        Тут можно зашить только ключевые параметры,
        которые нужны, чтобы повторить.
        """
        style = result.style_used.value if result.style_used else "any"
        city = result.weather.city if result.weather else "auto"
        return f"outfit:retry:{style}:{city}"
