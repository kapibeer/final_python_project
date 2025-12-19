from typing import List
from domain.models.user import User
from commands.manage_user_preferences import ManageUserPreferencesResult
from .types import RenderMessage, RenderButton
from datetime import time


class ManageUserPreferencesRenderer:
    """
    Рендерит результат обновления настроек пользователя.
    """

    def render(self, result: ManageUserPreferencesResult) -> RenderMessage:
        if not result.success:
            return self._render_error(result.message_key)

        if result.message_key == "updated":
            return self._render_updated(result.user)

        return RenderMessage(
            text="Что-то пошло не так 😔",
            buttons=[[RenderButton("🏠 Меню", "menu:home")]],
        )

    # -------------------- success --------------------

    def _render_updated(self, user: User) -> RenderMessage:
        text = "✅ Настройки обновлены!\n\n" + self._render_user_summary(user)

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

    def _render_user_summary(self, user: User) -> str:
        lines: List[str] = []

        lines.append(f"• Ник: {user.username}")
        lines.append(f"• Пол: {user.gender}")
        lines.append(f"• Возраст: {user.age}")
        lines.append(f"• Город: {user.location}")

        # cold sensitivity
        if user.cold_sensitivity is not None:
            lines.append(
                f"• Мерзлявость: {user.cold_sensitivity.value}"
            )

        # favourite style
        if user.favourite_style is not None:
            lines.append(
                f"• Любимый стиль: {user.favourite_style.value}"
            )

        # notification time
        if isinstance(user.notification_time, time):
            lines.append(
                f"• Время уведомлений: "
                f"{user.notification_time.strftime('%H:%M')}"
            )

        # notifications enabled
        str_enabled = 'включены' \
            if user.notifications_enabled else 'выключены'
        lines.append(
            f"• Уведомления {str_enabled}"
        )

        # seasonal notifications
        str_seasonal_enabled = 'включены' \
            if user.season_notifications_enabled else 'выключены'
        lines.append(
            f"• Сезонные уведомления {str_seasonal_enabled}"
        )
        return "\n".join(lines)
