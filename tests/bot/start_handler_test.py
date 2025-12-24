import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from domain.models.user import User, ColdSensitivity
from domain.models.clothing_item import Style

from bot.handlers.start import start


@pytest.mark.asyncio
async def test_start_existing_user_sends_welcome_and_menu() -> None:
    msg = SimpleNamespace()
    msg.text = "/start"
    msg.from_user = SimpleNamespace(id=123, username="kapaaa")
    msg.answer = AsyncMock()

    state = SimpleNamespace()
    state.clear = AsyncMock()

    user = User(
        user_id=123,
        username="muza",
        gender="male",
        age=1,
        location="TestCity",
        cold_sensitivity=ColdSensitivity.MEDIUM,
        notifications_enabled=True,
        season_notifications_enabled=True,
        last_season_notifiied=None,
        favourite_style=Style.CASUAL,
    )

    user_repo = SimpleNamespace()
    user_repo.get = AsyncMock(return_value=user)

    container = SimpleNamespace()
    container.user_repo = lambda: user_repo

    # --- act ---
    await start(msg, state, container)

    # --- assert ---
    state.clear.assert_awaited_once()
    user_repo.get.assert_awaited_once_with(123)

    msg.answer.assert_awaited()
    if msg.answer.await_args is None:
        return
    sent_text = msg.answer.await_args.kwargs["text"]  \
        if "text" in msg.answer.await_args.kwargs  \
        else msg.answer.await_args.args[0]
    assert "С возвращением" in sent_text
    assert "Что будем делать?" in sent_text
