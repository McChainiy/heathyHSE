from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from bot.config import DATABASE_URL
from sqlalchemy.ext.declarative import declarative_base

from contextlib import contextmanager

engine = create_engine(DATABASE_URL)


Base = declarative_base()


@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()