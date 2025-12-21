import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from infra.container import Container
from infra.database import make_session_factory, make_engine  # type: ignore

from adapters.database_adapters.models.base import Base

from adapters.database_adapters.models.user_table import UserTable  # noqa
from adapters.database_adapters.models.wardrobe_table import WardrobeTable  # noqa

from bot.handlers.start import router as start_router
from bot.handlers.wardrobe import router as wardrobe_router
from bot.handlers.menu import router as menu_router
from bot.handlers.preferences import router as prefs_router
from bot.handlers.season_mailing import router as season_router
from bot.handlers.build_outfit import router as outfit_router


async def main():
    bot = Bot(token=os.environ["BOT_TOKEN"])
    dp = Dispatcher(storage=MemoryStorage())

    engine = make_engine()
    session_factory = make_session_factory(engine)

    Base.metadata.create_all(bind=engine)

    container = Container(session_factory=session_factory)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(wardrobe_router)
    dp.include_router(menu_router)
    dp.include_router(prefs_router)
    dp.include_router(season_router)
    dp.include_router(outfit_router)

    await dp.start_polling(bot, container=container)  # type: ignore

if __name__ == "__main__":
    asyncio.run(main())
