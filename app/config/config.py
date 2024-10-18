import os
from datetime import timedelta


class Config:
    CELERY_BROKER_URL = os.getenv('REDIS_URL')
    DEBUG = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    # Mailer-To-Go SMTP configuration
    MAIL_SERVER = os.getenv('MAILERTOGO_SMTP_HOST', 'smtp.us-west-1.mailertogo.net')
    MAIL_PORT = int(os.getenv('MAILERTOGO_SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAILERTOGO_SMTP_USER')
    MAIL_PASSWORD = os.getenv('MAILERTOGO_SMTP_PASSWORD')

    NOTIFICATION_EMAIL_RECEIVERS = os.getenv('NOTIFICATION_EMAIL_RECEIVERS')
    NOTIFICATION_EMAIL_SENDER = f'{MAIL_USERNAME}@{MAIL_SERVER}'  # Use the Mailer-To-Go user as sender

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQL_ALCHEMY_TRACK_MODIFICATIONS = True
