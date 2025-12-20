from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup
from typing import List
from adapters.telegram_adapters.renderers.types import RenderButton


def text_kb(text: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def kb(rows: List[List[RenderButton]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for row in rows:
        kb.row(*[btn.to_aiogram() for btn in row])
    return kb.as_markup()
