from flask import jsonify
from flask_restful import Resource, reqparse, abort
from app.models import Parent
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.database import db
import os
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')

parent_parser = reqparse.RequestParser()
parent_parser.add_argument('parentName', type=str, required=True, help='Parent name is required')
parent_parser.add_argument('email', type=str, required=True, help='Email is required')
parent_parser.add_argument('phoneNumber', type=str, required=True, help='Phone number is required')
parent_parser.add_argument('athletes', type=list, location='json', default=[])

engine = create_engine(database_uri)  # Update with your database URI


class ParentResource(Resource):
    def post(self):
        args = parent_parser.parse_args()
        new_parent = Parent(
            parent_name=args['parent_name'],
            email=args['email'],
            phone_number=args['phone_number']
        )
        db.session.add(new_parent)
        try:
            db.session.commit()
            return jsonify(new_parent), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 500

    def get(self, parent_id):
        session = Session(bind=engine)
        athlete = session.query(Parent).filter(Parent.parent_id == parent_id).first()
        session.close()
        if athlete:
            return jsonify(athlete.to_dict())
        abort(404, message=f'Parent with ID {parent_id} not found')

    def put(self, parent_id):
        args = parent_parser.parse_args()
        session = Session(bind=engine)
        parent = session.query(Parent).filter(Parent.parent_id == parent_id).first()
        if parent:
            parent.full_name = args['parentFullName']
            parent.date_of_birth = datetime.strptime(args['dateOfBirth'], '%Y-%m-%d').date()
            parent.gender = args['gender']
            parent.returner_status = args['returner_status']
            session.commit()
            session.close()
            return jsonify(parent)
        session.close()
        abort(404, message=f'Parent with ID {parent_id} not found')

    def delete(self, parent_id):
        session = Session(bind=engine)
        parent = session.query(Parent).filter(Parent.parent_id == parent_id).first()
        if parent:
            session.delete(parent)
            session.commit()
            session.close()
            return '', 204
        session.close()
        abort(404, message=f'Parent with ID {parent_id} not found')
