# type: ignore
import pytest
from types import SimpleNamespace

from bot.handlers.daily_recommendation import send_daily_to_user


class FakeRendered:
    def __init__(self):
        self.text = "<b>hi</b>"
        self.keyboard = "KB"


class FakeDailyRenderer:
    def render(self, result):
        return FakeRendered()


class FakeDailyUsecase:
    def __init__(self, result):
        self._result = result
        self.calls = []

    async def run(self, user_id: int, today):
        self.calls.append((user_id, today))
        return self._result


class FakeContainer:
    def __init__(self, result):
        self._usecase = FakeDailyUsecase(result)

    def daily_recommendation(self):
        return self._usecase


class FakeBot:
    def __init__(self):
        self.sent_messages = []
        self.sent_photos = []

    async def send_message(self, chat_id,
                           text, reply_markup=None,
                           parse_mode=None):
        self.sent_messages.append(
            {"chat_id": chat_id, "text": text, "reply_markup": reply_markup,
             "parse_mode": parse_mode}
        )

    async def send_photo(self, chat_id,
                         photo, caption,
                         reply_markup=None,
                         parse_mode=None):
        self.sent_photos.append(
            {"chat_id": chat_id, "caption": caption,
             "reply_markup": reply_markup,
             "parse_mode": parse_mode}
        )


@pytest.mark.asyncio
async def test_send_daily_to_user_without_outfit(monkeypatch):
    # подменяем рендерер на лёгкий
    monkeypatch.setattr(
        "bot.handlers.daily_recommendation.DailyRecommendationRenderer",
        FakeDailyRenderer,
    )

    result = SimpleNamespace(outfit=None)  # минимально нужное поле
    bot = FakeBot()
    container = FakeContainer(result)

    await send_daily_to_user(bot,
                             container,
                             user_id=123)

    assert len(bot.sent_messages) == 1
    assert bot.sent_messages[0]["chat_id"] == 123
    assert bot.sent_messages[0]["parse_mode"] == "HTML"
    assert len(bot.sent_photos) == 0


@pytest.mark.asyncio
async def test_send_daily_to_user_with_outfit_sends_photo(monkeypatch):
    monkeypatch.setattr(
        "bot.handlers.daily_recommendation.DailyRecommendationRenderer",
        FakeDailyRenderer,
    )

    fake_outfit = SimpleNamespace(items=[])
    result = SimpleNamespace(outfit=fake_outfit)

    bot = FakeBot()
    container = FakeContainer(result)

    await send_daily_to_user(bot, container, user_id=123)

    assert len(bot.sent_photos) == 1
    assert bot.sent_photos[0]["chat_id"] == 123
    assert bot.sent_photos[0]["parse_mode"] == "HTML"
    assert len(bot.sent_messages) == 0
