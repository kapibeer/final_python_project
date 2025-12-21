from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from aiogram import Bot
from infra.container import Container
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from bot.handlers.daily_recommendation import send_daily_to_user
from bot.handlers.season_mailing import run_season_mailing


BOT_TZ = ZoneInfo("Europe/Moscow")


def _time_window_last_minute(now: datetime) -> tuple[time, time]:
    end_dt = now.replace(second=0, microsecond=0)
    start_dt = end_dt - timedelta(minutes=2)
    return (start_dt.time(), end_dt.time())


async def daily_tick(bot: Bot, container: Container) -> None:
    now = datetime.now(BOT_TZ)
    start_t, end_t = _time_window_last_minute(now)

    user_repo = container.user_repo()
    users = user_repo.get_users_to_notify_between(start=start_t, end=end_t)

    for u in users:
        if not u.notifications_enabled:
            continue
        try:
            await send_daily_to_user(bot, container, u.user_id)
        except Exception:
            pass


def setup_scheduler(bot: Bot, container: Container) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    scheduler.add_job(daily_tick,  # type: ignore
                      "interval", minutes=2,
                      args=[bot, container])

    scheduler.add_job(  # type: ignore
        lambda: run_season_mailing(bot, container),
        "cron",
        hour=12,
        minute=00,
    )

    return scheduler
