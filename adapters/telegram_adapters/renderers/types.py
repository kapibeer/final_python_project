from dataclasses import dataclass, field
from typing import Optional, Sequence
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass(frozen=True)
class RenderButton:
    text: str
    callback_data: Optional[str] = None
    url: Optional[str] = None

    def to_aiogram(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=self.text,
            callback_data=self.callback_data,
            url=self.url,
        )


@dataclass
class RenderMessage:
    text: str
    buttons: Optional[Sequence[Sequence[RenderButton]]] = None
    image_bytes: Optional[bytes] = None

    keyboard: Optional[InlineKeyboardMarkup] = field(init=False)

    def __post_init__(self):
        if not self.buttons:
            self.keyboard = None
            return

        kb = InlineKeyboardBuilder()
        for row in self.buttons:
            kb.row(*[btn.to_aiogram() for btn in row])

        self.keyboard = kb.as_markup()
