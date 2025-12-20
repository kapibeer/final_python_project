from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


def make_engine():
    return create_engine(
        os.environ["DATABASE_URL"],
        pool_pre_ping=True,
    )


def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
