import logging
import os

from flask_sqlalchemy import SQLAlchemy

from .config import Config
from .database import create_tables
from .database.engine import init_engine
from .models import *
from .resources import initialize_routes
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv
from celery import Celery
from .database import db

# Profiler uncomment when needed
# from werkzeug.middleware.profiler import ProfilerMiddleware

mail = Mail()
migrate = Migrate()
JWTManager = JWTManager()


# Function to create Flask app
def create_app():
    # noinspection PyShadowingNames
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config)

    api = Api(app)
    initialize_routes(api)
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager.init_app(app)

    with app.app_context():
        init_engine()

    return app


# Initialize Flask application
app = create_app()
# create_tables(app)

# Uncomment Profiler when needed
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app)


# TODO: ABSTRACT CELERY INTO ITS OWN MODULE WITHOUT BREAKING CELERY... AGAIN..
# noinspection PyShadowingNames
def make_celery(app):
    broker_url = os.getenv('REDIS_URL')

    cel = Celery(app.import_name, backend=broker_url, broker=broker_url)

    class ContextTask(cel.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # noinspection PyPropertyAccess
    cel.Task = ContextTask
    return cel


celery_app = make_celery(app)
celery_app.conf.broker_url = os.getenv("REDIS_URL")
app.logger.setLevel(logging.DEBUG)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    header['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    header['Access-Control-Allow-Credentials'] = 'true'
    return response
