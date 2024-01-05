from sqlalchemy import create_engine, inspect
from .base import Base  # Make sure this imports all your models
import os
from dotenv import load_dotenv

load_dotenv()

database_uri = os.getenv('DATABASE_URL')


def setup_database():
    engine = create_engine(database_uri)
    # Create an inspector to check for tables
    inspector = inspect(engine)

    # Only create tables that don't already exist
    for table_name in Base.metadata.tables.keys():
        if not inspector.has_table(table_name):
            Base.metadata.tables[table_name].create(engine)


if __name__ == "__main__":
    setup_database()
