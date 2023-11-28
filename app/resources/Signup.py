import os
from datetime import datetime

from flask import jsonify, request
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models import Athlete, Parent
from app.utils.CalculateAge import calculate_age
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

        for athlete_data in data['athletes']:
            # TODO: parse data to be filled in pdf

            new_athlete = Athlete(
                full_name=athlete_data['athleteFullName'],
                date_of_birth=datetime.strptime(athlete_data['dateOfBirth'], '%Y-%m-%d').date(),
                gender=athlete_data['gender'],
                returner_status=athlete_data['returner_status'],
                parent_id=new_parent.parent_id
            )

            db.session.add(new_athlete)

            # Determine checkbox values based on gender
            if new_athlete.gender.lower() == 'male':
                boy = '/Yes'
                girl = '/Off'
            else:
                boy = '/Off'
                girl = '/Yes'

            # TODO: add insurance info when added to frontend form
            # Insurance fields:
            # Carrier[0]
            # Policy_Number[0]
            # Employer[0]

            # Populate the PDF form data
            pdf_form_data = {
                'track[0]': '/Yes',
                'cross_country[0]': '/Off',
                'boy[0]': boy,
                'girl[0]': girl,
                'Age[0]': str(calculate_age(new_athlete.date_of_birth)),
                'Players_Name[0]': new_athlete.full_name,
                'Date_of_Birth[0]': new_athlete.date_of_birth.strftime('%m/%d/%Y'),
                # Assuming 'Date_Signed' is the current date
                'Date_Signed[0]': datetime.now().strftime('%m/%d/%Y'),
                'Players_Address[0]': str(data['streetAddress']),  # Replace with actual parent address field
                'City__Zip[0]': str(data['city'] + "  " + data['zipcode']),
                'Phone[0]': new_parent.phone_number,
                'Email[0]': new_parent.email,
                'Cell_PhoneEmergency[0]': data['emergencyPhone'],
                'Contact[0]': data['emergencyName'],
                'I_declare_under_penalty_of_perjury_that_I_am_a_parent_or_guardian_of[0]': new_athlete.full_name,
                'Name_Parent_or_Guardian_print[0]': new_parent.parent_name,
                'Date[0]': datetime.now().strftime('%m/%d/%Y'),

            }

            try:
                db.session.commit()
                # Fill the PDF form for the athlete
                output_file = f"contract_{new_athlete.full_name}.pdf"  # Naming the PDF file
                process_pdf = ProcessPdf(temp_directory, output_file)
                # TODO: Add correct data remove athlete_data
                process_pdf.add_data_to_pdf('app/pdfforms/PLAYER_CONTRACT.pdf', pdf_form_data)
                pdf_link = os.path.join(request.url_root, temp_directory, output_file)  # Construct the link to the PDF
                pdf_links.append(pdf_link)
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'message': 'Error creating athlete', 'error': str(e)}, 500

        return jsonify({'message': 'Sign up successful'}), 201
