from flask import Flask, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from app.models import Parent, Athlete
from .database import init_db
from flask_cors import CORS
from .resources import AthleteResource
from .resources import SignupResource
from .database import db
import os
from dotenv import load_dotenv

load_dotenv()

database_uri = os.getenv('DATABASE_URL')

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # to suppress a warning message

db.init_app(app)

# Run DB setup
init_db.setup_database()

# Flask-Mail Configs
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'malcolmloveless@gmail.com'
app.config['MAIL_PASSWORD'] = 'jcch wzuz wblr bhtl'

# Resource for athletes
api.add_resource(AthleteResource, '/athletes/<int:athlete_id>')
# Resource for signup page
api.add_resource(SignupResource,'/signup')


if __name__ == '__main__':
    app.run()
