from bot.keyboards.keyboard_helper import kb
from adapters.telegram_adapters.renderers.types import RenderButton
from aiogram.types import InlineKeyboardMarkup


EditKeyboard: InlineKeyboardMarkup = kb([
        [RenderButton("📍 Поменять город", "outfit:edit:location")],
        [RenderButton("🛍 Поменять стиль", "outfit:edit:style")],
        [RenderButton("📆 Поменять дату", "outfit:edit:date")],
        [RenderButton("💎 Всё готово!", "outfit:gen")],
        [RenderButton("🏠 Меню", "menu:home")],
    ])


StyleKeyboard = kb([
                    [
                        RenderButton("👕 Кэжуал", "outfit:style:casual"),
                        RenderButton("🧥 Официальный", "outfit:style:official"),
                    ],
                    [
                        RenderButton("🏃 Спортивный", "outfit:style:sport"),
                        RenderButton("🎉 Вечерний", "outfit:style:party"),
                    ],
                    [
                        RenderButton("🛹 Уличный", "outfit:style:street"),
                        RenderButton("🌲 Aутдор", "outfit:style:outdoor"),
                    ],
                    [RenderButton("⬅️ Назад", "outfit:build")]
                ])

DateQuickKeyboard: InlineKeyboardMarkup = kb([
    [RenderButton("Сегодня", "outfit:date:today"),
     RenderButton("Завтра", "outfit:date:tomorrow")],
    [RenderButton("⬅️ Назад", "outfit:build")]])


LikeKeyboard: InlineKeyboardMarkup = kb([
                        [RenderButton("✨ Подобрать еще лук", "outfit:build")],
                        [RenderButton("🌟 Получить рекомендацию на сегодня",
                                      "daily:build")],
                        [
                            RenderButton("🧥 Гардероб", "wardrobe:open"),
                            RenderButton("⚙️ Настройки", "prefs:open"),
                        ]])
