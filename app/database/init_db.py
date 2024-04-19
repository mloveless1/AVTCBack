import os
from dotenv import load_dotenv
from .database import db

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')


def create_tables(app):
    with app.app_context():
        # This will create all tables that do not already exist
        db.create_all()


if __name__ == "__main__":
    setup_database()
