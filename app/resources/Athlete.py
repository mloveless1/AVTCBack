from flask import jsonify
from flask_restful import Resource, reqparse, abort
from app.models import Athlete
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.database import db


engine = create_engine('mysql+pymysql://root:Iamnotmalo12!@localhost/avtc')  # Update with your database URI

# Request parser for creating/updating Athlete resources
athlete_parser = reqparse.RequestParser()
athlete_parser.add_argument('athleteFullName', type=str, required=True, help='Athlete name is required')
athlete_parser.add_argument('dateOfBirth', type=str, required=True, help='Date of birth is required')
athlete_parser.add_argument('gender', type=str, required=True, choices=('male', 'female'))
athlete_parser.add_argument('returner_status', type=str, required=True, choices=('new', 'returner'))


# Resource class for managing Athletes

class AthleteResource(Resource):
    def post(self):
        args = athlete_parser.parse_args()
        new_athlete = Athlete(
            full_name=args['full_name'],
            date_of_birth=args['date_of_birth'],
            gender=args['gender'],
            returner_status=args['returner_status'],
            email=args['email'],
            phone_number=args['phone_number']
        )
        db.session.add(new_athlete)
        try:
            db.session.commit()
            return jsonify(new_athlete.to_dict()), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 500

    def get(self, athlete_id):
        session = Session(bind=engine)
        athlete = session.query(Athlete).filter(Athlete.athlete_id == athlete_id).first()
        session.close()
        if athlete:
            return jsonify(athlete.to_dict())
        abort(404, message=f'Athlete with ID {athlete_id} not found')

    def put(self, athlete_id):
        args = athlete_parser.parse_args()
        session = Session(bind=engine)
        athlete = session.query(Athlete).filter(Athlete.athlete_id == athlete_id).first()
        if athlete:
            athlete.full_name = args['athleteFullName']
            athlete.date_of_birth = datetime.strptime(args['dateOfBirth'], '%Y-%m-%d').date()
            athlete.gender = args['gender']
            athlete.returner_status = args['returner_status']
            session.commit()
            session.close()
            return jsonify(athlete)
        session.close()
        abort(404, message=f'Athlete with ID {athlete_id} not found')

    def delete(self, athlete_id):
        session = Session(bind=engine)
        athlete = session.query(Athlete).filter(Athlete.athlete_id == athlete_id).first()
        if athlete:
            session.delete(athlete)
            session.commit()
            session.close()
            return '', 204
        session.close()
        abort(404, message=f'Athlete with ID {athlete_id} not found')
