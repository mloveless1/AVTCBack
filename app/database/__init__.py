from .init_db import create_tables
from .database import db
from .engine import engine
from sqlalchemy.orm import Session


def get_session() -> Session:
    return Session(bind=engine)


