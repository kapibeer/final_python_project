from __future__ import annotations

from aiogram import Router, F, Bot
from aiogram.types import Message

from infra.container import Container
from commands.season_mailing import SeasonMailing
from adapters.telegram_adapters.renderers.season_mailing_renderer import (
    SeasonMailingRenderer,
)

router = Router()


@router.message(F.text == "/season_mailing")
async def season_mailing_cmd(msg: Message, bot: Bot, container: Container) \
        -> None:
    """
    Ручной запуск сезонной рассылки командой.
    """
    usecase: SeasonMailing = container.season_mailing()
    renderer = SeasonMailingRenderer()

    results = usecase.run()

    sent = 0
    failed = 0

    for r in results:
        rendered = renderer.render(r)

        try:
            await bot.send_message(
                chat_id=r.user_id,
                text=rendered.text,
                reply_markup=rendered.keyboard,
            )
            sent += 1
        except Exception:
            failed += 1

    print(
        f"✅ Season mailing done.\n"
        f"Sent: {sent}\nFailed: {failed}"
    )
