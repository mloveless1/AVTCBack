import logging
import base64
import os
from dotenv import load_dotenv
from datetime import datetime

from flask import request, current_app
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import db
from app.models import Athlete, Parent
from app.utils.CalculateAge import calculate_age, calculate_age_in_year
from app.utils.CalculateDivision import calculate_division
from app.utils.ProcessPdf import ProcessPdf
from app.utils.EmailNotification import EmailNotification

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')
email_sender = os.getenv('NOTIFICATION_EMAIL_SENDER')
email_receivers = os.getenv('NOTIFICATION_EMAIL_RECEIVERS').split(';')

engine = create_engine(database_uri)  # Update with your database URI


class SignupResource(Resource):
    def post(self):
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

        db.session.add(new_parent)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Failed on creating parent: {e}", exc_info=True)
            return {'message': 'Error creating parent', 'error': str(e)}, 500

        pdf_links = []
        temp_directory = '/tmp'
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

        # Initialize sign up summary
        signup_summary = "Signup Summary:\n"

        for athlete_data in data['athletes']:

            new_athlete = Athlete(
                full_name=athlete_data['athleteFullName'],
                date_of_birth=datetime.strptime(athlete_data['dateOfBirth'], '%Y-%m-%d').date(),
                gender=athlete_data['gender'],
                returner_status=athlete_data['returner_status'],
                parent_id=new_parent.parent_id
            )

            db.session.add(new_athlete)

            athlete_age = calculate_age(new_athlete.date_of_birth)
            athlete_age_in_year = calculate_age_in_year(new_athlete.date_of_birth)
            athlete_division = calculate_division(athlete_age_in_year)

            signup_summary += f"Name: {new_athlete.full_name}, Division: {athlete_division}\n"

            # Determine checkbox values based on gender
            if new_athlete.gender == 'male':
                boy = 'X'
                girl = ' '
            else:
                boy = ' '
                girl = 'X'

            # TODO: Add division Divisions[0]
            # Populate the PDF form data
            player_contract_form_data = {
                'KidSig': new_athlete.full_name,
                'Year': '24',
                'TeamName': 'Antelope Valley Track Club',
                'TrackFieldBox': 'Yes',
                'Boy': boy,
                'Girl': girl,
                'Age': str(athlete_age),
                'Division': athlete_division,
                'PlayersName': new_athlete.full_name,
                'Date of Birth': new_athlete.date_of_birth.strftime('%m/%d/%Y'),
                'Age_2': str(athlete_age),
                # Assuming 'Date_Signed' is the current date
                'DateSigned': datetime.now().strftime('%m/%d/%Y'),
                'PlayersAddress': str(data['streetAddress']),  # Replace with actual parent address field
                'CityZip': str(data['city'] + "  " + data['zipcode']),
                'Phone': new_parent.phone_number,
                'Email': new_parent.email,
                'Cell PhoneEmergency': data['emergencyPhone'],
                'Contact': data['emergencyName'],
                'Carrier': data['carrier'],
                'Policy Number': data['policyNumber'],
                # Stupid lazy "hack" to align the text on the form correctly
                'PlayerName2':
                    ("                                        " + new_athlete.full_name),
                'Name_Parent_or_Guardian_print[0]': "                    " + new_parent.parent_name,
                'Date Signed': datetime.now().strftime('%m/%d/%Y'),
                'NameOfParent': new_parent.parent_name,
            }

            code_of_conduct_form_data = {
                'PLAYER': new_athlete.full_name,
                'CLUB': 'Antelope Valley Track Club',
                'My Child 1': new_athlete.full_name,
                'My Child 2': athlete_data['medicalConditions'],
                'DATED': athlete_data['lastPhysical'],
                'Player Name Please Print': new_athlete.full_name,
                'Parents Name Please Print': data['parentName'],
                'CoachClub Officials Name Please Print': 'Tameisha Warner',
            }

            try:
                db.session.commit()

                # Create names for output files
                code_of_conduct_output_file = f"code_of_conduct{new_athlete.full_name}.pdf"
                output_file = f"contract_{new_athlete.full_name}.pdf"

                # Process pdf objects
                process_pdf = ProcessPdf(temp_directory, output_file)
                process_conduct_pdf = ProcessPdf(temp_directory, code_of_conduct_output_file)

                # Add data to pdf forms
                process_conduct_pdf.add_data_to_pdf('app/pdfforms/CODE_OF_CONDUCT.pdf', code_of_conduct_form_data)
                process_pdf.add_data_to_pdf('app/pdfforms/PLAYER_CONTRACT.pdf', player_contract_form_data)

                # Make paths to pdfs
                path_to_conduct_pdf = os.path.join(temp_directory, code_of_conduct_output_file)
                path_to_pdf = os.path.join(temp_directory, output_file)

                # Add signature to pages - Update these x, y, width, height values as needed
                process_pdf.embed_image_to_pdf(signature_img_path, path_to_pdf, x=80, y=171, width=80, height=35)
                process_conduct_pdf.embed_image_to_pdf(signature_img_path, path_to_conduct_pdf, x=250, y=45, width=80,
                                                       height=35)

                # Construct pdf link and append to pdf link list
                pdf_path = os.path.join(temp_directory, output_file)
                pdf_links.append(pdf_path)
                pdf_links.append(path_to_conduct_pdf)

            except SQLAlchemyError as e:
                db.session.rollback()
                return {'message': 'Error creating athlete', 'error': str(e)}, 500

        # Construct email
        email_helper = EmailNotification(current_app)

        subject = '{parent} signed up for AV Track Club'.format(parent=new_parent.parent_name)
        body = f'Contracts are attached below, not formatted for mobile devices.\n\n{signup_summary}'
        recipients = email_receivers
        sender = email_sender

        # Send email
        email_helper.send_email(subject=subject,
                                sender=sender,
                                recipients=recipients,
                                body=body,
                                pdf_paths=pdf_links)

        return {'message': 'Sign up successful'}, 201
