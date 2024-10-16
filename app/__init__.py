import os
from dotenv import load_dotenv
from celery import Celery

if os.path.exists('.env'):
    load_dotenv()

# For whatever reason if you remove this it will break celery.
# Although, we don't use this object at all.
# So just leave it alone for now until we rewrite our celery module.
celery = Celery(__name__, broker=os.getenv("REDIS_URL"), backend=os.getenv("REDIS_URL"))
