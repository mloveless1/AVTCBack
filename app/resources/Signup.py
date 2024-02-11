import base64
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import request
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import db
from app.models import Athlete, Parent
from app.tasks import send_async_email, process_pdf_async
from app.utils.CalculateAge import calculate_age, calculate_age_in_year
from app.utils.CalculateDivision import calculate_division

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')
email_sender = os.getenv('NOTIFICATION_EMAIL_SENDER')
email_receivers = os.getenv('NOTIFICATION_EMAIL_RECEIVERS').split(';')

engine = create_engine(database_uri)  # Update with your database URI


# noinspection PyMethodMayBeStatic
class SignupResource(Resource):
    def post(self):
        logging.info("Spinning up sign up")
        session = Session(bind=engine)

        data = request.get_json()

        new_parent = Parent(
            parent_name=data['parentName'],
            email=data['email'],
            phone_number=data['phoneNumber']
        )

        existing_parent = session.query(Parent).filter(Parent.email == data['email']).first()
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
            athlete_instance = Athlete(
                parent_id=new_parent.parent_id,
                full_name=athlete_data['athleteFullName'],
                date_of_birth=datetime.strptime(athlete_data['dateOfBirth'], '%Y-%m-%d').date(),
                gender=athlete_data['gender'],
                returner_status=athlete_data['returner_status'],
            )
            athlete_age_in_year = calculate_age_in_year(athlete_instance.date_of_birth)
            athlete_division = calculate_division(athlete_age_in_year)
            athletes_data.append(athlete_instance)
            signup_summary += f"Name: {athlete_instance.full_name}, Division: {athlete_division}\n"
        try:
            db.session.bulk_save_objects(athletes_data)
            db.session.commit()
        except SQLAlchemyError as e:
            logging.error(f"Failed on saving new athlete data: {e}", exc_info=True)
            return {'message': 'Error creating athletes', 'error': str(e)}, 500

        pdf_links = []
        signature_dir = '/tmp/signature_images'  # Update this path as needed

        if not os.path.exists(signature_dir):
            os.makedirs(signature_dir)

        # Decode and save the parent signature image
        signature_data = data['signature']
        signature_img = base64.b64decode(signature_data.split(',')[1])
        signature_img_path = os.path.join(signature_dir, 'temp_signature.png')

        try:
            with open(signature_img_path, 'wb') as img_file:
                img_file.write(signature_img)
        except IOError as e:
            logging.error(f"Couldn't write image: {e}", exc_info=True)
            return {'message': 'Error saving signature image', 'error': str(e)}, 500

        for athlete in athletes_data:

            athlete_age = calculate_age(athlete.date_of_birth)
            athlete_division = calculate_division(calculate_age_in_year(athlete.date_of_birth))
            form_data = self.get_athlete_form_data(athlete, new_parent, data, athlete_age, athlete_division)

            output_file_contract = f"contract_{athlete.full_name}.pdf"
            output_file_code_of_conduct = f"code_of_conduct_{athlete.full_name}.pdf"
            # Enqueue PDF processing tasks
            process_pdf_async.delay(
                athlete_data=form_data['player_contract_form_data'],
                signature_img_path=signature_img_path,
                template_path='app/pdfforms/PLAYER_CONTRACT.pdf',
                output_file=output_file_contract,
                x=80, y=171, width=80, height=35
            )
            process_pdf_async.delay(
                athlete_data=form_data['code_of_conduct_form_data'],
                signature_img_path=signature_img_path,
                template_path='app/pdfforms/CODE_OF_CONDUCT.pdf',
                output_file=output_file_code_of_conduct,
                x=250, y=45, width=80, height=35  # Adjust as needed
            )

        # build email
        subject = '{parent} signed up for AV Track Club'.format(parent=new_parent.parent_name)
        body = f'Contracts are attached below, not formatted for mobile devices.\n\n{signup_summary}'
        recipients = email_receivers
        sender = email_sender

        logging.info("Sending async email")

        send_async_email(subject=subject,
                         sender=sender,
                         recipients=recipients,
                         body=body,
                         pdf_paths=pdf_links)
        return {'message': 'Sign up successful'}, 201

    def get_athlete_form_data(self, athlete: Athlete, parent: Parent,
                              data: any, athlete_age: int, athlete_division: str, med_cond='', last_phy='') -> dict:
        data_dict = {}
        # Determine checkbox values based on gender
        boy, girl = ('X', ' ') if athlete.gender == 'male' else (' ', 'X')

        # TODO: Add division Divisions[0]
        # Populate the PDF form data
        player_contract_form_data = {
            'KidSig': athlete.full_name,
            'Year': '24',
            'TeamName': 'Antelope Valley Track Club',
            'TrackFieldBox': 'Yes',
            'Boy': boy,
            'Girl': girl,
            'Age': str(athlete_age),
            'Division': athlete_division,
            'PlayersName': athlete.full_name,
            'Date of Birth': athlete.date_of_birth.strftime('%m/%d/%Y'),
            'Age_2': str(athlete_age),
            # Assuming 'Date_Signed' is the current date
            'DateSigned': datetime.now().strftime('%m/%d/%Y'),
            'PlayersAddress': str(data['streetAddress']),  # Replace with actual parent address field
            'CityZip': str(data['city'] + "  " + data['zipcode']),
            'Phone': parent.phone_number,
            'Email': parent.email,
            'Cell PhoneEmergency': data['emergencyPhone'],
            'Contact': data['emergencyName'],
            'Carrier': data['carrier'],
            'Policy Number': data['policyNumber'],
            # Stupid lazy "hack" to align the text on the form correctly
            'PlayerName2':
                ("                                        " + athlete.full_name),
            'Name_Parent_or_Guardian_print[0]': "                    " + parent.parent_name,
            'Date Signed': datetime.now().strftime('%m/%d/%Y'),
            'NameOfParent': parent.parent_name,
        }
        data_dict['player_contract_form_data'] = player_contract_form_data

        code_of_conduct_form_data = {
            'PLAYER': athlete.full_name,
            'CLUB': 'Antelope Valley Track Club',
            'My Child 1': athlete.full_name,
            'My Child 2': med_cond,
            'DATED': last_phy,
            'Player Name Please Print': athlete.full_name,
            'Parents Name Please Print': parent.parent_name,
            'CoachClub Officials Name Please Print': 'Tameisha Warner',
        }
        data_dict['code_of_conduct_form_data'] = code_of_conduct_form_data

        return data_dict
