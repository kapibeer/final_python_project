import pytest
from types import SimpleNamespace

from domain.models.user import User, ColdSensitivity
from domain.models.clothing_item import Style

from bot.handlers.preferences import prefs


class FakeState:
    def __init__(self):
        self.cleared = False

    async def clear(self) -> None:
        self.cleared = True


class FakeUserRepo:
    def __init__(self, user: User | None):
        self._user = user

    async def get(self, user_id: int):
        return self._user


class FakeContainer:
    def __init__(self, user: User | None):
        self._repo = FakeUserRepo(user)

    def user_repo(self):
        return self._repo


class FakeMessage:
    def __init__(self):
        self.calls = []

    async def answer(self, text: str,
                     reply_markup=None,  # type: ignore
                     **kwargs):  # type: ignore
        self.calls.append(  # type: ignore
            {"text": text, "reply_markup": reply_markup, "kwargs": kwargs}
        )


class FakeCallbackQuery:
    def __init__(self, user_id: int, message: FakeMessage | None = None):
        self.from_user = SimpleNamespace(id=user_id)
        self.message = message
        self.answered = False

    async def answer(self, *args, **kwargs):  # type: ignore
        self.answered = True


def make_user() -> User:
    return User(
        user_id=1,
        username="test",
        gender="female",
        age=20,
        location="TestCity",
        cold_sensitivity=ColdSensitivity.MEDIUM,
        notifications_enabled=True,
        season_notifications_enabled=True,
        last_season_notifiied=None,
        favourite_style=Style.CASUAL,
    )


@pytest.mark.asyncio
async def test_prefs_user_found_sends_settings():
    state = FakeState()
    msg = FakeMessage()
    cb = FakeCallbackQuery(user_id=1, message=msg)

    container = FakeContainer(user=make_user())

    await prefs(cb, state, container)

    assert state.cleared is True
    assert cb.answered is True
    assert len(msg.calls) == 1  # type: ignore
    assert "🎛 НАСТРОЙКИ" in msg.calls[0]["text"]  # type: ignore


@pytest.mark.asyncio
async def test_prefs_user_not_found_asks_start():
    state = FakeState()
    msg = FakeMessage()
    cb = FakeCallbackQuery(user_id=1, message=msg)

    container = FakeContainer(user=None)

    await prefs(cb, state, container)

    assert state.cleared is True
    assert cb.answered is True
    assert len(msg.calls) == 1  # type: ignore
    assert "/start" in msg.calls[0]["text"]  # type: ignore
