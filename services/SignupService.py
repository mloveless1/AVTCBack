# signup_service.py

import base64
import logging
import os
from datetime import datetime

from flask import current_app as app
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import db
from app.models import Athlete, Parent
from app.utils.build_pdf_data import BuildPDFData
from app.tasks import send_async_email, process_pdf_async
from app.utils.CalculateAge import calculate_age_in_year
from app.utils.CalculateDivision import calculate_division

# TODO REFACTOR AND INTEGRATE INTO SIGNUP ENDPOINT


class SignupService:
    def __init__(self):
        self.database_uri = app.config['DATABASE_URI']
        self.email_sender = app.config['NOTIFICATION_EMAIL_SENDER']
        self.email_receivers = app.config['NOTIFICATION_EMAIL_RECEIVERS'].split(';')

    def signup(self, data) -> dict:
        logging.info('Starting signup service')

        engine = create_engine(self.database_uri)
        session = Session(bind=engine)

        new_parent = Parent(
            first_name=data['parentFirstName'],
            last_name=data['parentLastName'],
            suffix=data['suffixName'],
            email=data['email'],
            phone_number=data['phoneNumber']
        )

        existing_parent = session.query(Parent).filter(Parent.email == data['email']).first()
        if existing_parent:
            return {'message': 'A user with this email already exists'}, 409

        try:
            db.session.add(new_parent)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Failed on creating parent: {e}", exc_info=True)
            return {'message': 'Error creating parent', 'error': str(e)}, 500

        signup_summary, athletes_data, pdf_links = self.process_athletes(data['athletes'], new_parent)

        try:
            db.session.bulk_save_objects(athletes_data)
        except SQLAlchemyError as e:
            logging.error(f"Failed on saving new athlete data: {e}", exc_info=True)
            return {'message': 'Error creating athletes', 'error': str(e)}, 500

        subject = f"{new_parent.first_name} {new_parent.last_name} signed up for AV Track Club"
        body = f'Contracts are attached below, not formatted for mobile devices.\n\n{signup_summary}'

        logging.info("Sending async email")
        send_async_email.delay(subject=subject, sender=self.email_sender,
                               recipients=self.email_receivers, body=body, pdf_paths=pdf_links)

        db.session.commit()
        return {'message': 'Sign up successful'}, 201

    def process_athletes(self, athletes_data, parent):
        signup_summary = "Signup Summary:\n"
        athletes_instances = []
        pdf_links = []

        for athlete_data in athletes_data:
            athlete_instance = Athlete(
                parent_id=parent.parent_id,
                first_name=athlete_data['athleteFirstName'],
                last_name=athlete_data['athleteLastName'],
                suffix=athlete_data['suffixName'],
                date_of_birth=datetime.strptime(athlete_data['dateOfBirth'], '%Y-%m-%d').date(),
                gender=athlete_data['gender'],
                returner_status=athlete_data['returner_status'],
            )
            athlete_full_name = ' '.join([athlete_instance.first_name, athlete_instance.last_name])
            athlete_age_in_year = calculate_age_in_year(athlete_instance.date_of_birth)
            athlete_division = calculate_division(athlete_age_in_year)
            athletes_instances.append(athlete_instance)
            signup_summary += f"Name: {athlete_full_name}, Division: {athlete_division}\n"
            pdf_links += self.generate_pdfs(athlete_instance, parent)

        return signup_summary, athletes_instances, pdf_links

