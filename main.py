import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from infra.container import Container
from infra.database import make_session_factory, make_engine

from adapters.database_adapters.models.base import Base

from adapters.database_adapters.models.user_table import UserTable  # noqa
from adapters.database_adapters.models.wardrobe_table import WardrobeTable  # noqa

from bot.handlers.start import router as start_router
from bot.handlers.wardrobe import router as wardrobe_router


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

    await dp.start_polling(bot, container=container)

if __name__ == "__main__":
    asyncio.run(main())
