from flask import Flask, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from app.models import Parent, Athlete
from .database import init_db
from flask_cors import CORS
from .resources import AthleteResource
from .resources import SignupResource
from .database import db

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Iamnotmalo12!@localhost/avtc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # to suppress a warning message

db.init_app(app)

# Run DB setup
init_db.setup_database()

# Resource for athletes
api.add_resource(AthleteResource, '/athletes/<int:athlete_id>')
# Resource for signup page
api.add_resource(SignupResource,'/signup')


if __name__ == '__main__':
    app.run()
