import base64
import logging
import os
from datetime import datetime

from flask import request, current_app as app
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import db
from app.models import Athlete, Parent, Address
from app.utils.build_pdf_data import BuildPDFData
from app.tasks import send_async_email, process_pdf_async
from app.utils.CalculateAge import calculate_age, calculate_age_in_year
from app.utils.CalculateDivision import calculate_division


class SignupResource(Resource):
    def post(self):
        with app.app_context():
            # Pull configuration from app config
            database_uri = app.config['SQLALCHEMY_DATABASE_URI']
            email_sender = app.config['NOTIFICATION_EMAIL_SENDER']
            email_receivers = app.config['NOTIFICATION_EMAIL_RECEIVERS']

        logging.info("Starting sign-up process")

        engine = create_engine(database_uri)
        session = Session(bind=engine)

        data = request.get_json()
        new_parent = self._create_parent(data)

        # Check if parent already exists
        existing_parent = session.query(Parent).filter(Parent.email == data['email']).first()
        if existing_parent:
            return {'message': 'A user with this email already exists'}, 409

        # Save new parent and address to DB
        try:
            db.session.add(new_parent)
            db.session.flush()

            new_address = self._create_address(new_parent.parent_id, data)
            db.session.add(new_address)
            db.session.flush()

        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Failed to create parent: {e}", exc_info=True)
            return {'message': 'Error creating parent', 'error': str(e)}, 500

        # Process PDFs and build signup summary
        pdf_links, signup_summary = self._process_athletes_and_generate_pdfs(data, new_parent)

        # Create and save athlete objects to DB
        try:
            athletes = self._create_athlete_objects(data, new_parent)
            db.session.bulk_save_objects(athletes)
        except SQLAlchemyError as e:
            logging.error(f"Failed to save athlete data: {e}", exc_info=True)
            return {'message': 'Error creating athletes', 'error': str(e)}, 500

        # Send confirmation email
        self._send_confirmation_email(new_parent, signup_summary, pdf_links, email_sender, email_receivers)

        # Commit transaction
        db.session.commit()
        return {'message': 'Sign up successful'}, 201

    def _create_parent(self, data):
        """Helper to create a Parent object."""
        return Parent(
            first_name=data['parentFirstName'],
            last_name=data['parentLastName'],
            suffix=data.get('suffixName', ''),
            email=data['email'],
            phone_number=data['phoneNumber']
        )

    def _create_address(self, parent_id, data):
        """Helper to create an Address object."""
        return Address(
            street_address=data['streetAddress'],
            city=data['city'],
            state='CA',
            zip_code=data['zipCode'],
            parent_id=parent_id,
        )


    def _process_athletes_and_generate_pdfs(self, data, parent):
        """Generate PDFs for athletes and build a signup summary."""
        pdf_links = []
        parent_full_name = ' '.join([data['parentFirstName'], data['parentLastName']])
        signup_summary = (f'Signup Summary:\n\n '
                          f'Parent: {parent_full_name}\n')

        parent_signature_data: base64 = data['parent_signature']
        parent_signature_img: bytes = base64.b64decode(parent_signature_data.split(',')[1])

        temp_directory = '/tmp'

        for athlete in data['athletes']:
            # Build athlete's name and calculate age/division
            athlete_full_name = ' '.join([
                athlete['athleteFirstName'],
                athlete['athleteLastName'],
                athlete.get('suffixName', '')
            ]).strip()

            athlete_birth_date = datetime.strptime(athlete['dateOfBirth'], '%Y-%m-%d').date()
            athlete_age = calculate_age(athlete_birth_date)
            athlete_age_in_year = calculate_age_in_year(athlete_birth_date, int(app.config['SEASON_YEAR']))
            athlete_division = calculate_division(athlete_age_in_year)

            # Add to signup summary
            signup_summary += f"Athlete name: {athlete_full_name}, Division: {athlete_division}\n"

            athlete_signature_data: base64 = athlete['athlete_signature']
            athlete_signature_img: bytes = base64.b64decode(athlete_signature_data.split(',')[1])

            # Initialize PDF data processor
            data_processor = BuildPDFData(**data)
            player_contract_data = data_processor.get_player_contract_form_data(athlete, int(app.config['SEASON_YEAR']))
            code_of_conduct_data = data_processor.get_code_of_conduct_form_data(athlete)

            # Generate file names for PDFs
            code_of_conduct_output_file = f"code_of_conduct_{athlete_full_name}.pdf"
            player_contract_output_file = f"player_contract_{athlete_full_name}.pdf"

            # Template paths
            coc_template = 'app/pdfforms/CODE_OF_CONDUCT.pdf'
            plyr_template = 'app/pdfforms/PLAYER_CONTRACT.pdf'

            # Process PDFs asynchronously
            process_pdf_async.delay(
                athlete_data=code_of_conduct_data,
                parent_signature_img_data=parent_signature_img,
                athlete_signature_img_data=athlete_signature_img,
                template_path=coc_template,
                output_file=code_of_conduct_output_file,
                x=250, y=45, width=80, height=35
            )

            process_pdf_async.delay(
                athlete_data=player_contract_data,
                parent_signature_img_data=parent_signature_img,
                athlete_signature_img_data=athlete_signature_img,
                template_path=plyr_template,
                output_file=player_contract_output_file,
                x=80, y=171, width=80, height=35
            )

            # Add PDF paths to the list
            pdf_links.extend([
                os.path.join(temp_directory, code_of_conduct_output_file),
                os.path.join(temp_directory, player_contract_output_file)
            ])

        return pdf_links, signup_summary

    def _create_athlete_objects(self, data, parent):
        """Create a list of Athlete objects."""
        athletes = []
        for athlete_data in data['athletes']:
            athlete = Athlete(
                parent_id=parent.parent_id,
                first_name=athlete_data['athleteFirstName'],
                last_name=athlete_data['athleteLastName'],
                suffix=athlete_data.get('suffixName', ''),
                date_of_birth=datetime.strptime(athlete_data['dateOfBirth'], '%Y-%m-%d').date(),
                gender=athlete_data['gender'],
                returner_status=athlete_data['returner_status'],
                medical_conditions=athlete_data.get('medicalConditions', '')
            )
            athletes.append(athlete)
        return athletes

    def _send_confirmation_email(self, parent, signup_summary, pdf_links, sender, recipients):
        """Send a confirmation email with the generated PDFs."""
        subject = f"Successful sign up for AV Track Club"
        body = f"Contracts are attached below, not formatted for mobile devices.\n\n{signup_summary}"

        logging.info("Sending async email")
        send_async_email.delay(
            subject=subject,
            sender=sender,
            recipients=recipients,
            body=body,
            pdf_paths=pdf_links
        )

    def sign_contracts():
        # TODO MOVE CONTRACT LOGIC TO HERE
        pass
