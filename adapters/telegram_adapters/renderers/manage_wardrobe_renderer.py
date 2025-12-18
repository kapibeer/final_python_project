# renderers/manage_wardrobe.py

from typing import List
from domain import ClothingItem
from commands.manage_wardrobe import ManageWardrobeResult
from .types import RenderMessage, RenderButton


class ManageWardrobeRenderer:
    """
    Рендерит результат управления гардеробом:
    добавление / обновление / удаление вещи.
    """

    def render(self, result: ManageWardrobeResult) -> RenderMessage:
        if not result.success:
            return self._render_error(result.message_key)

        if result.message_key == "added":
            return self._render_added(result.item)

        if result.message_key == "updated":
            return self._render_updated(result.item)

        if result.message_key == "deleted":
            return self._render_deleted()

        return RenderMessage(
            text="Что-то пошло не так 😔",
            buttons=[[RenderButton("🧥 Гардероб", "wardrobe:open")],
                     [RenderButton("🏠 Меню", "menu:home")],
                     ],
        )

    # -------------------- success cases --------------------

    def _render_added(self, item: ClothingItem) -> RenderMessage:
        text = (
            "✨ Вещь добавлена в гардероб!\n\n"
            + self._render_item(item)
        )

        buttons = [
            [RenderButton("➕ Добавить ещё", "wardrobe:add")],
            [RenderButton("🧥 Гардероб", "wardrobe:open"),
             RenderButton("🏠 Меню", "menu:home")],
        ]

        return RenderMessage(text=text, buttons=buttons)

    def _render_updated(self, item: ClothingItem) -> RenderMessage:
        text = (
            "✏️ Вещь обновлена!\n\n"
            + self._render_item(item)
        )

        buttons = [
            [RenderButton("🧥 Гардероб", "wardrobe:open"),
             RenderButton("🏠 Меню", "menu:home")],
        ]

        return RenderMessage(text=text, buttons=buttons)

    def _render_deleted(self) -> RenderMessage:
        text = "🗑 Вещь удалена из гардероба."

        buttons = [
            [RenderButton("🧥 Гардероб", "wardrobe:open"),
             RenderButton("🏠 Меню", "menu:home")],
        ]

        return RenderMessage(text=text, buttons=buttons)

    # -------------------- error cases --------------------

    def _render_error(self, message_key: str) -> RenderMessage:
        if message_key == "not_found":
            return RenderMessage(
                text="Я не нашёл эту вещь 😶\n"
                     "Возможно, она уже была удалена.",
                buttons=[
                    [RenderButton("🧥 Гардероб", "wardrobe:open")],
                    [RenderButton("🏠 Меню", "menu:home")],
                ],
            )

        return RenderMessage(
            text="Что-то пошло не так 😔",
            buttons=[
                    [RenderButton("🧥 Гардероб", "wardrobe:open")],
                    [RenderButton("🏠 Меню", "menu:home")],
                ],
        )

    # -------------------- helpers --------------------

    def _render_item(self, item: ClothingItem) -> str:
        """
        Короткое текстовое описание вещи.
        """
        lines: List[str] = [
            f"• Название: {item.name}"
            f"• Категория: {item.category.value}",
            f"• Тип: {item.subtype.value}",
            f"• Стиль: {item.style.value}",
            f"• Цвет: {item.main_color.value}",
            f"• Теплота: {item.warmth_level.value}",
        ]
        return "\n".join(lines)
