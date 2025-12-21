from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.keyboards import menu_keyboards


router = Router()


@router.callback_query(F.data == "menu:home")
async def menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    if cb.message is not None:
        await cb.message.answer(
                    "🏠 <b>Меню</b>",
                    reply_markup=menu_keyboards.MenuKeyboard,
                    parse_mode="HTML")
    await cb.answer()
