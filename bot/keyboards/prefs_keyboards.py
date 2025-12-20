from bot.keyboards.keyboard_helper import kb
from adapters.telegram_adapters.renderers.types import RenderButton
from aiogram.types import InlineKeyboardMarkup


PrefsKeyboard: InlineKeyboardMarkup = kb([
        [RenderButton("👤 Пол", "prefs:edit:gender")],
        [RenderButton("🎂 Возраст", "prefs:edit:age")],
        [RenderButton("📍 Город", "prefs:edit:location")],
        [RenderButton("🥶 Мерзлявость", "prefs:edit:cold")],
        [RenderButton("🎛 Любимый стиль", "prefs:edit:style")],
        [RenderButton("🔔 Ежедневные уведомления", "prefs:edit:notif")],
        [RenderButton("🍂 Сезонные уведомления", "prefs:edit:season_notif")],
        [RenderButton("⏰ Время уведомлений", "prefs:edit:time")],
        [RenderButton("🏠 Меню", "menu:home")],
    ])
