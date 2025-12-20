from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def text_kb(text: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def _kb(rows):
    kb = InlineKeyboardBuilder()
    for row in rows:
        kb.row(*[btn.to_aiogram() for btn in row])
    return kb.as_markup()
