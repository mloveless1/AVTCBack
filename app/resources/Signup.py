import base64
import os
from datetime import datetime

from flask import jsonify, request
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models import Athlete, Parent
from app.utils.CalculateAge import calculate_age
from app.utils.CalculateDivision import calculate_division
from app.utils.ProcessPdf import ProcessPdf

engine = create_engine('mysql+pymysql://root:Iamnotmalo12!@localhost/avtc')  # Update with your database URI


class SignupResource(Resource):
    def post(self):
        data = request.get_json()

        new_parent = Parent(
            parent_name=data['parentName'],
            email=data['email'],
            phone_number=data['phoneNumber']
        )

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

        # Decode and save the signature image
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
            pdf_form_data = {
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
                'I_declare_under_penalty_of_perjury_that_I_am_a_parent_or_guardian_of[0]':
                    ("                                        " + new_athlete.full_name),
                'Name_Parent_or_Guardian_print[0]': "                    " + new_parent.parent_name,
                'Date[0]': datetime.now().strftime('%m/%d/%Y'),
            }

            try:
                db.session.commit()

                # Fill the PDF form for the athlete
                output_file = f"contract_{new_athlete.full_name}.pdf"
                process_pdf = ProcessPdf(temp_directory, output_file)
                process_pdf.add_data_to_pdf('app/pdfforms/PLAYER_CONTRACT.pdf', pdf_form_data)
                path_to_pdf = os.path.join(temp_directory, output_file)

                # Update these x, y, width, height values as needed
                process_pdf.embed_image_to_pdf(signature_img_path, path_to_pdf, x=80, y=100, width=200, height=100)

                pdf_link = os.path.join(request.url_root, temp_directory, output_file)  # Construct the link to the PDF
                pdf_links.append(pdf_link)

            except SQLAlchemyError as e:
                db.session.rollback()
                return {'message': 'Error creating athlete', 'error': str(e)}, 500

        return {'message': 'Sign up successful'}, 201
