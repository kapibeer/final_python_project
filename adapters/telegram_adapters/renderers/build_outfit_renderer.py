from typing import List
from domain.models.outfit import Outfit
from commands.build_outfit import BuildOutfitResult
from .types import RenderMessage, RenderButton
from dataclasses import dataclass


@dataclass(frozen=True)
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
            buttons: List[List[RenderButton]] = [
                [RenderButton("🔁 Сгенерировать ещё",
                              "outfit:gen")],
                [RenderButton("🧥 Гардероб", "wardrobe:open"),
                 RenderButton("🏠 Меню", "menu:home")],
                [],
            ]
        else:
            buttons = [
                [
                    RenderButton("👍 Нравится", "outfit:like"),
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
                              "outfit:gen")],
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
        if w.is_rain:
            icons.append("🌧")
        if w.is_snow:
            icons.append("❄️")
        if w.is_windy:
            icons.append("💨")
        icons_str = (" ".join(icons) + " ") if icons else ""

        location = w.city
        dt = w.required_date
        date_str = dt.isoformat() if hasattr(dt, "isoformat") else ""

        t_m = w.temp_morning
        t_d = w.temp_day
        t_e = w.temp_evening

        return (
            f"{location} • {date_str.replace('-', '.')}\n"
            f"{icons_str}\n☀️  Утро ~ {t_m}°\n ⛅️ День ~ {t_d}°\n"
            f"🌙  Вечер ~ {t_e}°\n"
            f"Стиль: {st}"
        ).strip()

    def _render_outfit(self, outfit: Outfit, idx: int, total: int) -> str:
        lines: List[str] = ["Аутфит для тебя! 💋 \n"]
        for item in outfit.items:
            lines.append(
                f"•{item.name}: {item.subtype.value}"
                f" · {item.style.value} · {item.main_color.value}"
            )
        return "\n".join(lines)
