from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from adapters.telegram_adapters.renderers.types import RenderButton
from bot.keyboards.keyboard_helper import kb


router = Router()


@router.callback_query(F.data == "menu:home")
async def menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    if cb.message is not None:
        await cb.message.answer(
                    "🏠 Меню",
                    reply_markup=kb([
                        [RenderButton("✨ Подобрать лук", "outfit:build")],
                        [RenderButton("🌟 Получить рекомендацию на сегодня",
                                      "daily:build")],
                        [
                            RenderButton("🧥 Гардероб", "wardrobe:open"),
                            RenderButton("⚙️ Настройки", "prefs:open"),
                        ]]))
