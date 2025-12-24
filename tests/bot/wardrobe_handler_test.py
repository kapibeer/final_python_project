# type: ignore
import pytest

from bot.handlers.wardrobe import wardrobe_add, ClothingItemSetup


class DummyState:
    def __init__(self) -> None:
        self.cleared = False
        self.state = None
        self.data: dict = {}

    async def clear(self) -> None:
        self.cleared = True
        self.state = None
        self.data = {}

    async def set_state(self, s) -> None:
        self.state = s

    async def update_data(self, **kwargs) -> None:
        self.data.update(kwargs)


class DummyUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


class DummyMessage:
    def __init__(self) -> None:
        self.answers: list[tuple[str, object]] = []

    async def answer(self,
                     text: str,
                     reply_markup=None, **kwargs) -> None:
        self.answers.append((text, reply_markup))


class DummyCallbackQuery:
    def __init__(self) -> None:
        self.message = DummyMessage()
        self.from_user = DummyUser(123)

    async def answer(self, *args, **kwargs) -> None:
        return


@pytest.mark.asyncio
async def test_wardrobe_add_sets_state_and_asks_name() -> None:
    cb = DummyCallbackQuery()
    state = DummyState()

    await wardrobe_add(cb, state)

    assert state.cleared is True
    assert state.state == ClothingItemSetup.name
    assert state.data["mode"] == "add"

    assert len(cb.message.answers) == 1
    text, _ = cb.message.answers[0]
    assert "Как назовём вещь" in text
