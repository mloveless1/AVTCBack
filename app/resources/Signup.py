import base64
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import request, current_app
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import db, get_session
from app.models import Athlete, Parent
from app.utils.build_pdf_data import BuildPDFData
from app.tasks import send_async_email, process_pdf_async
from app.utils.CalculateAge import calculate_age, calculate_age_in_year
from app.utils.CalculateDivision import calculate_division

if os.path.exists('.env'):
    load_dotenv()

# Refactor to pull from Config
database_uri = os.environ.get('DATABASE_URL')
email_sender = os.getenv('NOTIFICATION_EMAIL_SENDER')
email_receivers = os.getenv('NOTIFICATION_EMAIL_RECEIVERS').split(';')

engine = create_engine(database_uri)
# noinspection PyMethodMayBeStatic
class SignupResource(Resource):
    def post(self):
        logging.info("Starting sign up process")
        session = Session(bind=engine)

        data = request.get_json()

        new_parent: Parent = Parent(
            first_name=data['parentFirstName'],
            last_name=data['parentLastName'],
            suffix=data['suffixName'],
            email=data['email'],
            phone_number=data['phoneNumber']
        )

        existing_parent: Parent = session.query(Parent).filter(Parent.email == data['email']).first()
        if existing_parent:
            return {'message': 'A user with this email already exists'}, 409
        # Create new parent
        try:
            db.session.add(new_parent)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Failed on creating parent: {e}", exc_info=True)
            return {'message': 'Error creating parent', 'error': str(e)}, 500

        # Initialize sign up summary
        signup_summary = "Signup Summary:\n"

        athletes_data = []
        for athlete_data in data['athletes']:
            # Athlete object
            athlete_instance: Athlete = Athlete(
                parent_id=new_parent.parent_id,
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
            athletes_data.append(athlete_instance)
            signup_summary += f"Name: {athlete_full_name}, Division: {athlete_division}\n"

        # DB bulk save
        try:
            db.session.bulk_save_objects(athletes_data)
            db.session.commit()
        except SQLAlchemyError as e:
            logging.error(f"Failed on saving new athlete data: {e}", exc_info=True)
            return {'message': 'Error creating athletes', 'error': str(e)}, 500

        pdf_links = []

        # Decode signature img data
        signature_data: base64 = data['signature']
        signature_img: bytes = base64.b64decode(signature_data.split(',')[1])

        # temp directory in heroku do not change
        temp_directory = '/tmp'
        for athlete in athletes_data:
            parent_full_name = ' '.join([new_parent.first_name, new_parent.last_name,
                                         new_parent.suffix if new_parent.suffix is not None else ''])
            athlete_full_name = ' '.join([athlete.first_name, athlete.last_name,
                                          athlete.suffix if athlete.suffix is not None else ''])
            athlete_age = calculate_age(athlete.date_of_birth)
            athlete_division = calculate_division(calculate_age_in_year(athlete.date_of_birth))

            data_processor = BuildPDFData(**data)
            player_contract_data = data_processor.get_player_contract_form_data(athlete)
            code_of_conduct_data = data_processor.get_code_of_conduct_form_data(athlete)

            # Create names for output files
            code_of_conduct_output_file = f"code_of_conduct_{athlete_full_name}.pdf"
            plyr_contract_output_file = f"player_contract_{athlete_full_name}.pdf"

            # Templates pdfs to fill
            coc_template = 'app/pdfforms/CODE_OF_CONDUCT.pdf'
            plyr_template = 'app/pdfforms/PLAYER_CONTRACT.pdf'

            # Code of conduct
            process_pdf_async.delay(athlete_data=code_of_conduct_data,
                                    signature_img_data=signature_img,
                                    template_path=coc_template, output_file=code_of_conduct_output_file,
                                    x=250, y=45, width=80, height=35)

            # Player contract
            process_pdf_async.delay(athlete_data=player_contract_data,
                                    signature_img_data=signature_img,
                                    template_path=plyr_template, output_file=plyr_contract_output_file,
                                    x=80, y=171, width=80, height=35)

            # Construct pdf link and append to pdf link list
            pdf_path = os.path.join(temp_directory, plyr_contract_output_file)
            path_to_conduct_pdf = os.path.join(temp_directory, code_of_conduct_output_file)
            pdf_links.append(pdf_path)
            pdf_links.append(path_to_conduct_pdf)

        # build email
        subject = '{parent} signed up for AV Track Club'.format(
            parent=' '.join([new_parent.first_name, new_parent.last_name]))
        body = f'Contracts are attached below, not formatted for mobile devices.\n\n{signup_summary}'
        recipients = email_receivers
        sender = email_sender

        logging.info("Sending async email")

        send_async_email.delay(subject=subject,
                               sender=sender,
                               recipients=recipients,
                               body=body,
                               pdf_paths=pdf_links)
        return {'message': 'Sign up successful'}, 201
