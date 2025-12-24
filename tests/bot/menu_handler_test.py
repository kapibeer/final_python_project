# type: ignore
import pytest

from bot.handlers.menu import menu


class FakeState:
    def __init__(self) -> None:
        self.cleared = 0

    async def clear(self) -> None:
        self.cleared += 1


class FakeMessage:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.calls.append({"text": text, **kwargs})


class FakeCallbackQuery:
    def __init__(self, message: FakeMessage | None) -> None:
        self.message = message
        self.answered = 0

    async def answer(self) -> None:
        self.answered += 1


@pytest.mark.asyncio
async def test_menu_home_clears_state_and_sends_menu(monkeypatch) -> None:
    from bot.handlers import menu as menu_module

    monkeypatch.setattr(menu_module.menu_keyboards, "MenuKeyboard", object())

    state = FakeState()
    msg = FakeMessage()
    cb = FakeCallbackQuery(message=msg)

    await menu(cb, state)

    assert state.cleared == 1
    assert cb.answered == 1
    assert len(msg.calls) == 1

    call = msg.calls[0]
    assert call["text"] == "🏠 <b>Меню</b>"
    assert "reply_markup" in call
    assert call["parse_mode"] == "HTML"


@pytest.mark.asyncio
async def test_menu_home_when_no_message_only_answers(monkeypatch) -> None:
    state = FakeState()
    cb = FakeCallbackQuery(message=None)

    await menu(cb, state)

    assert state.cleared == 1
    assert cb.answered == 1
