import base64
import os
from datetime import datetime

from flask import request, current_app
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import db
from app.models import Athlete, Parent
from app.utils.CalculateAge import calculate_age
from app.utils.CalculateDivision import calculate_division
from app.utils.ProcessPdf import ProcessPdf
from app.utils.EmailNotification import EmailNotification

engine = create_engine('mysql+pymysql://root:Iamnotmalo12!@localhost/avtc')  # Update with your database URI


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
            return {'message': 'Error creating parent', 'error': str(e)}, 500

        pdf_links = []
        temp_directory = 'app/pdfforms/output_files'
        signature_dir = 'app/pdfforms/signature_images'  # Update this path as needed

        if not os.path.exists(signature_dir):
            os.makedirs(signature_dir)

        # Decode and save the parent signature image
        signature_data = data['signature']
        signature_img = base64.b64decode(signature_data.split(',')[1])
        signature_img_path = 'app/pdfforms/signature_images/temp_signature.png'

        try:
            with open(signature_img_path, 'wb') as img_file:
                img_file.write(signature_img)
        except IOError as e:
            return {'message': 'Error saving signature image', 'error': str(e)}, 500

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
            athlete_division = calculate_division(athlete_age)
            # Determine checkbox values based on gender
            if new_athlete.gender == 'male':
                boy = '/1'
                girl = 'Off'
            else:
                boy = 'Off'
                girl = '/1'

            # TODO: Add division Divisions[0]
            # Populate the PDF form data
            player_contract_form_data = {
                'track[0]': 'On',
                'cross_country[0]': '/Off',
                'boy[0]': boy,
                'girl[0]': girl,
                'Age[0]': str(athlete_age),
                'Divisions[0]': athlete_division,
                'Players_Name[0]': new_athlete.full_name,
                'Date_of_Birth[0]': new_athlete.date_of_birth.strftime('%m/%d/%Y'),
                'Age_2[0]': str(athlete_age),
                # Assuming 'Date_Signed' is the current date
                'Date_Signed[0]': datetime.now().strftime('%m/%d/%Y'),
                'Players_Address[0]': str(data['streetAddress']),  # Replace with actual parent address field
                'City__Zip[0]': str(data['city'] + "  " + data['zipcode']),
                'Phone[0]': new_parent.phone_number,
                'Email[0]': new_parent.email,
                'Cell_PhoneEmergency[0]': data['emergencyPhone'],
                'Contact[0]': data['emergencyName'],
                'Carrier[0]': data['carrier'],
                'Policy_Number[0]': data['policyNumber'],
                # Stupid lazy "hack" to align the text on the form correctly
                'I_declare_under_penalty_of_perjury_that_I_am_a_parent_or_guardian_of[0]':
                    ("                                        " + new_athlete.full_name),
                'Name_Parent_or_Guardian_print[0]': "                    " + new_parent.parent_name,
                'Date[0]': datetime.now().strftime('%m/%d/%Y'),
            }

            code_of_conduct_form_data = {
                'PLAYER': new_athlete.full_name,
                'CLUB': 'Antelope Valley Track Club',
                'My Child 1': new_athlete.full_name,
                'My Child 2': athlete_data['medicalConditions'],
                'DATED': athlete_data['lastPhysical'],
                'Player Name Please Print': new_athlete.full_name,
                'Parents Name Please Print': data['parentName'],
                'CoachClub Officials Name Please Print':  'Tameisha Warner',
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
                process_pdf.embed_image_to_pdf(signature_img_path, path_to_pdf, x=80, y=100, width=80, height=35)
                process_conduct_pdf.embed_image_to_pdf(signature_img_path, path_to_conduct_pdf, x=250, y=45, width=80, height=35)

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
        body = 'Contracts are attached below, not formatted for mobile devices.'
        recipients = ['malc.loveless@gmail.com']

        # Send email
        email_helper.send_email(subject=subject,
                                sender='malcolmloveless@gmail.com',
                                recipients=recipients,
                                body=body,
                                pdf_paths=pdf_links)

        return {'message': 'Sign up successful'}, 201
