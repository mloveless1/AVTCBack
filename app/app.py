from flask import Flask, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from app.models import Parent, Athlete
from .database import init_db
from flask_cors import CORS
from .resources import AthleteResource
from .database import db

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Iamnotmalo12!@localhost/avtc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # to suppress a warning message

db.init_app(app)

init_db.setup_database()

api.add_resource(AthleteResource, '/athletes/<int:athlete_id>')


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/create-dummy')
def create_dummy():  # put application's code here
    # Create a dummy parent
    parent = Parent(
        parent_id=1,  # Assuming `parent_id` is the primary key and is not auto-generated
        email='parent@example.com',
        phone_number='123-456-7890'
    )

    # Create a dummy athlete
    athlete = Athlete(
        athlete_id=1,  # Assuming `athlete_id` is the primary key and is not auto-generated
        full_name='Dummy Athlete',
        date_of_birth='2010-01-01',  # Use the appropriate format for your date column
        gender='male',
        returner_status='new',
        parent_id=1  # This assumes the Athlete model has a `parent_id` foreign key
    )

    # Add both records to the session and commit
    db.session.add(parent)
    db.session.add(athlete)

    try:
        db.session.commit()
        print("Dummy data inserted successfully!")
    except Exception as e:
        db.session.rollback()
        print("An error occurred while inserting dummy data:", e)
    return jsonify({"Message": "Dummy data created"})


if __name__ == '__main__':
    app.run()
