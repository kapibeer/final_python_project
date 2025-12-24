from typing import List
from domain.models.outfit import Outfit
from domain.models.clothing_item import Style
from commands.build_outfit import BuildOutfitResult
from .types import RenderMessage, RenderButton
from dataclasses import dataclass
import random
import adapters.telegram_adapters.renderers.translates as translates


OUTFIT_LIKED_WISHES_BY_STYLE = {
    Style.CASUAL: [
        "Комфортно и со вкусом 🙂",
        "Очень спокойный, приятный образ ✨",
        "В таком луке легко провести весь день 👌",
        "Смотрится естественно и ненавязчиво 🤍",
        "Просто, удобно и стильно — хороший баланс 😌",
    ],

    Style.OFFICIAL: [
        "Собранно и уверенно 💼",
        "Строго, но без лишней сухости ✨",
        "Образ выглядит аккуратно и профессионально 👌",
        "Добавляет уверенности с первого взгляда 🤍",
        "Чисто, по делу и со вкусом 🖤",
    ],

    Style.SPORT: [
        "Удобно и выглядит бодро 🏃‍♂️",
        "Комфорт чувствуется сразу 👌",
        "Практично и без лишней суеты ✨",
        "Подходит для активного дня 💪",
        "Лёгкий и функциональный образ 😌",
    ],

    Style.PARTY: [
        "Есть настроение, и оно читается ✨",
        "Смотрится эффектно, но не перегружено 💫",
        "Образ цепляет, но остаётся стильным 😌",
        "В таком приятно выйти вечером 🌙",
        "Немного вау, но со вкусом 🔥",
    ],

    Style.STREET: [
        "Есть характер — и это чувствуется 😎",
        "Городской вайб без лишнего шума 🖤",
        "Смотрится уверенно и расслабленно ✨",
        "Простой, но запоминающийся образ 👌",
        "Очень органично для улицы 🌆",
    ],

    Style.OUTDOOR: [
        "Практично и по-настоящему удобно 🌿",
        "Комфортно даже при долгой прогулке 👌",
        "Готов к погоде и движению 💨",
        "Надёжно и аккуратно выглядит ✨",
        "Уютно и функционально 🤍",
    ],
}


def renderer_like(style: Style) -> str:
    base = "Рада, что тебе понравилось! 💖"
    comment = random.choice(
        OUTFIT_LIKED_WISHES_BY_STYLE.get(style, ["Хороший выбор ✨"])
    )

    return f"{base}\n{comment}"


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
                [RenderButton("👍 Нравится", "outfit:like")],
                [RenderButton("➕ Добавить вещь", "wardrobe:add")],
                [RenderButton("🏠 Меню", "menu:home")],
            ],
        )

    def _render_header(self, result: BuildOutfitResult) -> str:
        w = result.weather
        st = result.style_used.value if result.style_used else "any"
        st = result.style_used.value if result.style_used else ""
        style_tr = "Любой"
        if st:
            style_tr = translates.STYLE_TRANSLATE[st]

        if not w:
            return f"Стиль: {style_tr}"

        icons: List[str] = []
        if w.is_rain:
            icons.append("🌧")
        if w.is_snow:
            icons.append("❄️")
        if w.is_windy:
            icons.append("💨")
        icons_str = (" ".join(icons) + " ") if icons else "❎"

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
            f"<b>Стиль:</b> {style_tr}"
            )

    def _render_outfit(self, outfit: Outfit, idx: int, total: int) -> str:
        lines: List[str] = ["<blockquote>Aутфит для тебя 💋 </blockquote>\n"]
        for item in outfit.items:
            lines.append(
                f"• <b>{item.name}</b>"
            )
        return "\n".join(lines)
