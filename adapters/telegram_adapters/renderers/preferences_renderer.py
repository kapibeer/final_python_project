from typing import List
from domain.models.user import User
from commands.manage_user_preferences import ManageUserPreferencesResult
from .types import RenderMessage, RenderButton
from dataclasses import dataclass
import adapters.telegram_adapters.renderers.translates as translates


@dataclass(frozen=True)
class ManageUserPreferencesRenderer:
    """
    Рендерит результат обновления настроек пользователя.
    """

    def render(self, result: ManageUserPreferencesResult) -> RenderMessage:
        if not result.success:
            return self._render_error(result.message_key)

        if result.message_key == "updated" and result.user is not None:
            return self._render_updated(result.user)

        return RenderMessage(
            text="Что-то пошло не так 😔",
            buttons=[[RenderButton("🏠 Меню", "menu:home")]],
        )

    # -------------------- success --------------------

    def _render_updated(self, user: User) -> RenderMessage:
        text = "✅ Настройки обновлены!\n\n"

        buttons = [
            [RenderButton("🎛 Настройки", "prefs:open")],
            [RenderButton("🏠 Меню", "menu:home")],
        ]

        return RenderMessage(text=text, buttons=buttons)

    # -------------------- errors --------------------

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

    # -------------------- helpers --------------------

    def render_user_summary(self, user: User) -> str:
        lines: List[str] = []
        lines.append(f"• Ник: {user.username}")
        lines.append(f"• Пол: {'👩' if user.gender == 'female' else '👨'}")
        lines.append(f"• Возраст: {user.age}")
        lines.append(f"• Город: {user.location}")

        # cold sensitivity
        lines.append(
            "• Мерзлявость: "
            f"{translates.COLD_TRANSLATE [user.cold_sensitivity.value]}"
            )

        # favourite style
        lines.append(
                "• Любимый стиль: "
                f"{translates.STYLE_TRANSLATE[user.favourite_style.value]}"
        )

        # notification time
        lines.append(
                f"• Время уведомлений: "
                f"{user.notification_time.strftime('%H:%M')}"
            )

        # notifications enabled
        str_enabled = '✅' \
            if user.notifications_enabled else '❌'
        lines.append(
            f"• Уведомления: {str_enabled}"
        )

        # seasonal notifications
        str_seasonal_enabled = '✅' \
            if user.season_notifications_enabled else '❌'
        lines.append(
            f"• Сезонные уведомления: {str_seasonal_enabled}"
        )
        return "\n".join(lines)
