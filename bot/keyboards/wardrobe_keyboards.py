from bot.keyboards.keyboard_helper import kb
from adapters.telegram_adapters.renderers.types import RenderButton
from domain.repositories.wardrobe_repository import WardrobeRepository
from domain.models.clothing_item import ClothingItem
from typing import List
from aiogram.types import InlineKeyboardMarkup


WardrobeKeyboard = kb([
                    [RenderButton("Просмотреть вещи", "wardrobe:watch")],
                    [RenderButton("➕ Добавить вещь", "wardrobe:add")],
                    [RenderButton("✏️ Изменить вещь", "wardrobe:update")],
                    [RenderButton("🗑 Удалить вещь", "wardrobe:delete")],
                    [
                        RenderButton("🏠 Меню", "menu:home"),
                        RenderButton("⚙️ Настройки", "prefs:open"),
                    ],
                ])

# -----------------------------
# CATEGORY
# -----------------------------

CategoryKeyboard = kb([
    [
        RenderButton("🧥 Верхняя одежда", "item:cat:outerwear"),
        RenderButton("👕 Верх", "item:cat:top"),
        RenderButton("👖 Низ", "item:cat:bottom"),
    ],
    [
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


# -----------------------------
# TOP SUBTYPES
# -----------------------------

TopSubtypeKeyboard = kb([
    [
        RenderButton("Футболка", "item:subtype:tshirt"),
        RenderButton("Лонгслив", "item:subtype:longsleeve"),
        RenderButton("Майка", "item:subtype:tank_top"),
    ],
    [
        RenderButton("Кардиган", "item:subtype:cardigan"),
        RenderButton("Рубашка", "item:subtype:shirt"),
        RenderButton("Пиджак", "item:subtype:blazer"),
    ],
    [
        RenderButton("Зипка", "item:subtype:zip_hoodie"),
        RenderButton("Водолазка", "item:subtype:turtleneck"),
        RenderButton("Худи", "item:subtype:hoodie"),
    ],
    [
        RenderButton("Платье", "item:subtype:dress"),
        RenderButton("Комбинезон", "item:subtype:jumpsuit"),
        RenderButton("Боди", "item:subtype:bodysuit")
    ],
    [
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


# -----------------------------
# BOTTOM SUBTYPES
# -----------------------------

BottomSubtypeKeyboard = kb([
    [
        RenderButton("Джинсы", "item:subtype:jeans"),
        RenderButton("Брюки", "item:subtype:trousers"),
    ],
    [
        RenderButton("Шорты", "item:subtype:shorts"),
        RenderButton("Юбка", "item:subtype:skirt"),
    ],
    [
        RenderButton("Спортивные штаны", "item:subtype:sweatpants"),
        RenderButton("Джоггеры", "item:subtype:joggers"),
    ],
    [
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


# -----------------------------
# OUTERWEAR SUBTYPES
# -----------------------------

OuterwearSubtypeKeyboard = kb([
    [
        RenderButton("Пальто", "item:subtype:coat"),
        RenderButton("Куртка", "item:subtype:jacket"),
    ],
    [
        RenderButton("Бомбер", "item:subtype:bomber"),
        RenderButton("Тренч", "item:subtype:trench"),
    ],
    [
        RenderButton("Пуховик", "item:subtype:puffer"),
        RenderButton("Шуба", "item:subtype:fur_coat"),
    ],
    [
        RenderButton("Дублёнка", "item:subtype:sheepskin_coat"),
        RenderButton("Ветровка", "item:subtype:windbreaker"),
    ],
    [
        RenderButton("Джинсовка", "item:subtype:jeans_jacket"),
        RenderButton("Косуха", "item:subtype:biker_jacket"),
    ],
    [
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


# -----------------------------
# COLORS
# -----------------------------

ColorKeyboard = kb([
    [
        RenderButton("Чёрный", "item:color:black"),
        RenderButton("Белый", "item:color:white"),
        RenderButton("Серый", "item:color:grey"),
    ],
    [
        RenderButton("Бежевый", "item:color:beige"),
        RenderButton("Коричневый", "item:color:brown"),
        RenderButton("Синий", "item:color:navy"),
    ],
    [
        RenderButton("Красный", "item:color:red"),
        RenderButton("Зелёный", "item:color:green"),
        RenderButton("Фиолетовый", "item:color:purple"),
    ],
    [
        RenderButton("Желтый", "item:color:yellow"),
        RenderButton("Голубой", "item:color:blue"),
        RenderButton("Оранжевый", "item:color:orange"),
    ],
    [
        RenderButton("Розовый", "item:color:pink"),
        RenderButton("Хаки", "item:color:khaki"),
        RenderButton("Разноцветный", "item:color:multicolor"),
    ],
    [
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


# -----------------------------
# STYLE
# -----------------------------

StyleKeyboard = kb([
    [
        RenderButton("👕 Casual", "item:style:casual"),
        RenderButton("🧥 Official", "item:style:official"),
    ],
    [
        RenderButton("🏃 Sport", "item:style:sport"),
        RenderButton("🎉 Party", "item:style:party"),
    ],
    [
        RenderButton("🛹 Street", "item:style:street"),
        RenderButton("🌲 Outdoor", "item:style:outdoor"),
    ],
    [
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


# -----------------------------
# WARMTH
# -----------------------------

WarmthKeyboard = kb([
    [
        RenderButton("Лёгкая", "item:warmth:light"),
        RenderButton("Средняя", "item:warmth:medium"),
    ],
    [
        RenderButton("Тёплая", "item:warmth:warm"),
        RenderButton("Очень тёплая", "item:warmth:very_warm"),
    ],
    [
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


# -----------------------------
# WATER / WIND
# -----------------------------

YesNoKeyboard = kb([
    [
        RenderButton("✅ Да", "item:yes"),
        RenderButton("❌ Нет", "item:no"),
    ],
    [
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


# -----------------------------
# CONFIRM
# -----------------------------

ConfirmKeyboard = kb([
    [
        RenderButton("💾 Сохранить", "item:confirm:save"),
        RenderButton("❌ Отмена", "wardrobe:add:cancel"),
    ],
])


def UserItemsKeyboard(user_id: int, wardrobe_repo: WardrobeRepository,
                      action: str) -> InlineKeyboardMarkup:
    wardrobe: List[ClothingItem] = \
        wardrobe_repo.get_user_wardrobe(user_id=user_id)
    buttons: List[List[RenderButton]] = []
    for item in wardrobe:
        buttons.append([RenderButton(item.name,
                                     f"item:{action}:{item.item_id}")])
    buttons.append([RenderButton("🏠 Меню", "menu:home")])
    buttons.append([RenderButton("🧥 Гардероб", "wardrobe:open")])
    return kb(buttons)
