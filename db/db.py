from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.testing.schema import mapped_column
from bot.config import DATABASE_URL
from sqlalchemy.ext.declarative import declarative_base

from contextlib import contextmanager

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass


Base = declarative_base()


@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()