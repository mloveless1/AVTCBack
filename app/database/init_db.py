from sqlalchemy import create_engine
from .base import Base
import os
from dotenv import load_dotenv

load_dotenv()

database_uri = os.getenv('DATABASE_URL')


def setup_database():
    engine = create_engine(database_uri)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    setup_database()
