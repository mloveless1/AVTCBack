import os
from dotenv import load_dotenv
from celery import Celery

if os.path.exists('.env'):
    load_dotenv()

celery = Celery(__name__, broker=os.getenv("REDIS_URL"), backend=os.getenv("REDIS_URL"))
