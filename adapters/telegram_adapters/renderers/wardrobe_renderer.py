from domain.models.clothing_item import ClothingItem
from commands.manage_wardrobe import ManageWardrobeResult
from .types import RenderMessage, RenderButton
from typing import Any
import adapters.telegram_adapters.renderers.translates as translates


def item_summary(data: dict[Any, Any]) -> str:
    return (
        "Проверь, всё ок?\n\n"
        f"• Название: {data.get('name','-')}\n"
        f"• Категория: "
        f"{translates.CATEGORY_TRANSLATE[data.get('category','-')]}\n"
        f"• Подтип: {translates.SUBTYPE_TRANSLATE[data.get('subtype','-')]}\n"
        f"• Цвет: {translates.COLOR_TRANSLATE[data.get('main_color','-')]}\n"
        f"• Стиль: {translates.STYLE_TRANSLATE[data.get('style','-')]}\n"
        "• Теплота: "
        f"{translates.WARMTH_TRANSLATE[data.get('warmth_level', '-')]}\n"
        f"• Водозащита: {data.get('is_waterproof', False)}\n"
        f"• Ветрозащита: {data.get('is_windproof', False)}\n"
        f"• Фото: {'есть' if data.get('image_id') else 'нет'}")


def item_summary_domain(item: ClothingItem) -> str:
    return (
        f"• Название: {item.name}\n"
        f"• Категория: {translates.CATEGORY_TRANSLATE[item.category]}\n"
        f"• Подтип: {translates.SUBTYPE_TRANSLATE[item.subtype]}\n"
        f"• Цвет: {translates.COLOR_TRANSLATE[item.main_color]}\n"
        f"• Стиль: {translates.STYLE_TRANSLATE[item.style]}\n"
        f"• Теплота: {translates.WARMTH_TRANSLATE[item.warmth_level]}\n"
        f"• Водозащита: {'✅' if item.is_waterproof else '❌'}\n"
        f"• Ветрозащита: {'✅' if item.is_windproof else '❌'}\n")


class ManageWardrobeRenderer:
    """
    Рендерит результат управления гардеробом:
    добавление / обновление / удаление вещи.
    """

    def render(self, result: ManageWardrobeResult) -> RenderMessage:
        if not result.success:
            return self._render_error(result.message_key)
        if result.item is not None:
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
