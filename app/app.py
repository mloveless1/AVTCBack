import logging
import os
from .resources import initialize_routes
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv
from celery import Celery
from .database import db
# Profiler uncomment when needed
# from werkzeug.middleware.profiler import ProfilerMiddleware


if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')


# Function to create Flask app
def create_app():
    # noinspection PyShadowingNames
    # TODO: HIDE SMTP CREDENTIALS ASAP in env vars
    # TODO: ABSTRACT CONFIGS INTO THEIR OWN MODULE
    app = Flask(__name__, template_folder='../templates')
    app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'malcolmloveless@gmail.com'
    app.config['MAIL_PASSWORD'] = 'jcch wzuz wblr bhtl'

    CORS(app, resources={r"/*": {"origins": "*"}})

    Mail(app)
    db.init_app(app)
    JWTManager(app)
    api = Api(app)
    initialize_routes(api)

    return app


# Initialize your Flask application
app = create_app()

# Uncomment Profiler when needed
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

# TODO: ABSTRACT CELERY INTO ITS OWN MODULE
# noinspection PyShadowingNames
def make_celery(app):
    broker_url = app.config['CELERY_BROKER_URL']
    print("Broker URL:", broker_url)  # Add this line for debugging
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


@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def index_page():
    return jsonify({"Message": "You don't belong here, please leave thanks"})


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    header['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    header['Access-Control-Allow-Credentials'] = 'true'
    return response
