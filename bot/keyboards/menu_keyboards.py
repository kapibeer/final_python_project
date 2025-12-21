from bot.keyboards.keyboard_helper import kb
from adapters.telegram_adapters.renderers.types import RenderButton
from aiogram.types import InlineKeyboardMarkup


MenuKeyboard: InlineKeyboardMarkup = kb([
                        [RenderButton("✨ Подобрать лук", "outfit:build")],
                        [RenderButton("🌟 Получить рекомендацию на сегодня",
                                      "daily:build")],
                        [
                            RenderButton("🧥 Гардероб", "wardrobe:open"),
                            RenderButton("⚙️ Настройки", "prefs:open"),
                        ]])
