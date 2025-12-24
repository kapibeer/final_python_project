# type: ignore
import pytest

from bot.handlers.season_mailing import run_season_mailing
from commands.season_mailing import SeasonMailResult


# ---------- fakes ----------

class FakeBot:
    def __init__(self, fail: bool = False):
        self.sent: list[dict] = []
        self.fail = fail

    async def send_message(self, chat_id: int, text: str, reply_markup=None):
        if self.fail:
            raise RuntimeError("send failed")
        self.sent.append({
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup,
        })


class FakeSeasonMailing:
    def __init__(self, results: list[SeasonMailResult]):
        self._results = results

    async def run(self):
        return self._results


class FakeContainer:
    def __init__(self, mailing: FakeSeasonMailing):
        self._mailing = mailing

    def season_mailing(self):
        return self._mailing


class FakeRenderResult:
    def __init__(self, text: str):
        self.text = text
        self.keyboard = [["ok"]]


class FakeRenderer:
    def render(self, r: SeasonMailResult):
        return FakeRenderResult(text=f"season {r.season}")


@pytest.mark.asyncio
async def test_run_season_mailing_success(monkeypatch):
    results = [
        SeasonMailResult(user_id=1, season="winter"),
        SeasonMailResult(user_id=2, season="spring"),
    ]

    container = FakeContainer(
        FakeSeasonMailing(results)
    )
    bot = FakeBot()

    # подменяем реальный renderer
    monkeypatch.setattr(
        "adapters.telegram_adapters.renderers.season_mailing_renderer."
        "SeasonMailingRenderer",
        lambda: FakeRenderer()
    )

    sent, failed = await run_season_mailing(bot, container)

    assert sent == 2
    assert failed == 0
    assert len(bot.sent) == 2
    assert bot.sent[0]["chat_id"] == 1
    assert "❄️ " in bot.sent[0]["text"]


@pytest.mark.asyncio
async def test_run_season_mailing_send_fails(monkeypatch):
    results = [
        SeasonMailResult(user_id=1, season="winter"),
    ]

    container = FakeContainer(
        FakeSeasonMailing(results)
    )
    bot = FakeBot(fail=True)

    monkeypatch.setattr(
        "adapters.telegram_adapters.renderers.season_mailing_renderer."
        "SeasonMailingRenderer",
        lambda: FakeRenderer()
    )

    sent, failed = await run_season_mailing(bot, container)

    assert sent == 0
    assert failed == 1
