from sqlalchemy import create_engine, inspect
from .base import Base  # Make sure this imports all your models
import os
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')


def setup_database():
    engine = create_engine(database_uri)
    # Create an inspector to check for tables
    inspector = inspect(engine)

    # Define the order of table creation
    ordered_tables = ['parents', 'athletes']

    # Only create tables that don't already exist, in the specified order
    for table_name in ordered_tables:
        if not inspector.has_table(table_name):
            table = Base.metadata.tables[table_name]
            table.create(engine)


if __name__ == "__main__":
    setup_database()
