
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask import current_app

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')
if database_uri is None:
    raise Exception("Database URI not defined")

db = SQLAlchemy()
