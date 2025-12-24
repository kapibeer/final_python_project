# type: ignore
import pytest
from datetime import date

from domain.models.clothing_item import Style

from bot.handlers.build_outfit import outfit_build, outfit_gen


class FakeUser:
    def __init__(self, user_id: int = 1):
        self.user_id = user_id
        self.location = "TestCity"
        self.favourite_style = Style.CASUAL


class FakeUserRepo:
    def __init__(self, user=None):
        self._user = user

    async def get(self, user_id: int):
        return self._user


class FakeWeatherRepo:
    def __init__(self, weather=None):
        self._weather = weather

    def get_weather(self, required_date: date, city: str):
        return self._weather


class FakeBuildOutfit:
    async def run(self, **kwargs):
        raise AssertionError("BuildOutfit.run "
                             "не должен вызываться в этом тесте")


class FakeContainer:
    def __init__(self, user=None, weather=None):
        self._user_repo = FakeUserRepo(user)
        self._weather_repo = FakeWeatherRepo(weather)

    def user_repo(self):
        return self._user_repo

    def weather_repo(self):
        return self._weather_repo

    def build_outfit(self):
        return FakeBuildOutfit()


class FakeFSM:
    def __init__(self):
        self.data = {}
        self.cleared = False

    async def clear(self):
        self.cleared = True
        self.data = {}

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return dict(self.data)

    async def set_state(self, state):
        self.data["_state"] = state


class FakeMessage:
    def __init__(self):
        self.answers = []

    def _normalize(self, args, kwargs):
        text = kwargs.get("text")
        if text is None and args:
            text = args[0]

        return {
            "text": text,
            "parse_mode": kwargs.get("parse_mode"),
            "args": args,
            "kwargs": kwargs,
        }

    async def answer(self, *args, **kwargs):
        self.answers.append(self._normalize(args, kwargs))

    async def answer_photo(self, *args, **kwargs):
        text = kwargs.get("caption")
        if text is None and len(args) >= 2:
            text = args[1]
        rec = {"text": text, "args": args, "kwargs": kwargs}
        self.answers.append(rec)


class FakeFromUser:
    def __init__(self, user_id: int = 1):
        self.id = user_id


class FakeCallback:
    def __init__(self, user_id: int = 1):
        self.from_user = FakeFromUser(user_id)
        self.message = FakeMessage()
        self.data = "x"
        self.bot = object()

    async def answer(self):
        pass


@pytest.mark.asyncio
async def test_outfit_build_user_exists_sets_defaults_and_sends_intro():
    cb = FakeCallback(user_id=1)
    state = FakeFSM()
    container = FakeContainer(user=FakeUser())

    await outfit_build(cb, state, container)

    assert state.cleared is True
    assert state.data["outfit_location"] == "TestCity"
    assert state.data["outfit_style"] == Style.CASUAL.value
    assert state.data["outfit_date"] == date.today().isoformat()

    assert len(cb.message.answers) == 1
    sent = cb.message.answers[0]
    assert "Давай подберем тебе аутфит" in sent["text"]
    assert sent["parse_mode"] == "HTML"


@pytest.mark.asyncio
async def test_outfit_gen_when_weather_none_shows_error_and_returns():
    cb = FakeCallback(user_id=1)
    state = FakeFSM()

    await state.update_data(
        outfit_location="Nowhere",
        outfit_style=Style.CASUAL.value,
        outfit_date=date.today().isoformat(),
    )

    container = FakeContainer(user=FakeUser(), weather=None)

    await outfit_gen(cb, state, container)

    assert len(cb.message.answers) == 1
    sent = cb.message.answers[0]
    assert "Не смог получить погоду" in sent["text"]
