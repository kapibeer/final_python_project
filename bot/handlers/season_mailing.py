from aiogram import Bot
from infra.container import Container
from commands.season_mailing import SeasonMailing
from adapters.telegram_adapters.renderers.season_mailing_renderer \
    import SeasonMailingRenderer


async def run_season_mailing(bot: Bot, container: Container) \
        -> tuple[int, int]:
    usecase: SeasonMailing = container.season_mailing()
    renderer = SeasonMailingRenderer()

    results = usecase.run()
    sent = 0
    failed = 0

    for r in results:
        rendered = renderer.render(r)
        if not rendered.text.strip():
            continue
        try:
            await bot.send_message(
                chat_id=r.user_id,
                text=rendered.text,
                reply_markup=rendered.keyboard,
            )
            sent += 1
        except Exception:
            failed += 1

    return sent, failed
