import os

from flask import current_app
from sqlalchemy import create_engine, Engine


def get_engine() -> Engine:
    database_uri = os.getenv("DATABASE_URL")
    engine: Engine = create_engine(database_uri)
    return engine


engine = None


def init_engine():
    global engine
    engine = get_engine()