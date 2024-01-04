from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

database_uri = os.getenv('DATABASE_URL')


db = SQLAlchemy()
# Configure the database connection (replace with your database URL)
DATABASE_URL = "mysql+pymysql://root:Iamnotmalo12!@localhost/avtc"
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
