from domain.models.clothing_item import ClothingItem
from commands.manage_wardrobe import ManageWardrobeResult
from .types import RenderMessage, RenderButton


def _item_summary(data: dict) -> str:
    # аккуратно, чтобы не падать если чего-то нет
    return (
        "Проверь, всё ок?\n\n"
        f"• Название: {data.get('name','-')}\n"
        f"• Категория: {data.get('category','-')}\n"
        f"• Подтип: {data.get('subtype','-')}\n"
        f"• Цвет: {data.get('main_color','-')}\n"
        f"• Стиль: {data.get('style','-')}\n"
        f"• Теплота: {data.get('warmth_level','-')}\n"
        f"• Водозащита: {data.get('is_waterproof', False)}\n"
        f"• Ветрозащита: {data.get('is_windproof', False)}\n"
        f"• Фото: {'есть' if data.get('image_id') else 'нет'}")


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
