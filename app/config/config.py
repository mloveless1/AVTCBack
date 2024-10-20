import os
from datetime import timedelta

class Config:
    # Celery and JWT Configs
    CELERY_BROKER_URL = os.getenv('REDIS_URL')
    DEBUG = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    # Gmail SMTP configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # More Email configs
    NOTIFICATION_EMAIL_RECEIVERS = os.getenv('NOTIFICATION_EMAIL_RECEIVERS', '').split(';')
    NOTIFICATION_EMAIL_SENDER = MAIL_USERNAME

    # SQLAlchemy configs
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQL_ALCHEMY_TRACK_MODIFICATIONS = True

    # Year the season will be in
    SEASON_YEAR = os.getenv('SEASON_YEAR', '2025')
