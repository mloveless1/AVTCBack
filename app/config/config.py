import os
from datetime import timedelta


class Config:
    CELERY_BROKER_URL = os.getenv('REDIS_URL')
    DEBUG = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    NOTIFICATION_EMAIL_RECEIVERS = os.getenv('NOTIFICATION_EMAIL_RECEIVERS')
    NOTIFICATION_EMAIL_SENDER = os.getenv('NOTIFICATION_EMAIL_SENDER')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQL_ALCHEMY_TRACK_MODIFICATIONS = True


