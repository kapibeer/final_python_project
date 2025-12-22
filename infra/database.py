from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os


def make_engine():
    return create_async_engine(
        os.environ["DATABASE_URL"],
        pool_pre_ping=True,
    )


def make_session_factory(engine):  # type: ignore
    return async_sessionmaker(
        engine,  # type: ignore
        autoflush=False,
        expire_on_commit=False,
    )
