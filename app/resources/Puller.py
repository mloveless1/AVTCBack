import os
import io
import csv
import logging
from datetime import datetime

from flask import Response
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Athlete, Parent, Address
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()


class PullerResource(Resource):
    @jwt_required()
    def get(self):
        # Load database URI from environment variable
        database_uri = os.getenv('DATABASE_URL')

        # Create a database engine and session
        engine = create_engine(database_uri)
        session = Session(bind=engine)

        try:
            # Perform a query to join Athlete, Parent, and Address based on parent_id
            query = (
                session.query(Athlete, Parent, Address)
                .outerjoin(Parent, Athlete.parent_id == Parent.parent_id)
                .outerjoin(Address, Parent.parent_id == Address.parent_id)
            )

            try:
                results = query.all()
            except Exception as e:
                logging.exception("Error performing join query")
                return {'error': 'Database query failed'}, 500

            # Create a CSV in memory
            output = io.StringIO()
            writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

            team_abbr = "AVTC"
            team_name = "ANTELOPE VALLEY TRACK CLUB"

            for athlete, parent, address in results:
                athlete_name_tokens = athlete.to_dict().get('full_name', '').split()
                first_name = athlete_name_tokens[0].capitalize().strip() if athlete_name_tokens else ''
                last_name = athlete_name_tokens[1] if len(athlete_name_tokens) > 1 else ''

                suffix = ''
                if len(athlete_name_tokens) == 3:
                    suffix = ' ' + athlete_name_tokens[2]

                last_name = (last_name + suffix).title().strip()

                # Handle gender conversion
                gender = 'M' if athlete.gender == 'male' else 'F' if athlete.gender == 'female' else ''

                # Convert date_of_birth to mm/dd/yyyy format
                try:
                    date_of_birth_obj = datetime.strptime(str(athlete.date_of_birth), '%Y-%m-%d')
                    formatted_date_of_birth = date_of_birth_obj.strftime('%m/%d/%Y')
                except ValueError:
                    formatted_date_of_birth = ''

                parent_name = parent.to_dict().get('full_name', '') if parent else 'N/A'
                email = parent.email if parent else 'N/A'
                phone = parent.phone_number if parent else 'N/A'

                # Extract address fields
                street_address = address.street_address if address else 'N/A'
                city = address.city if address else 'N/A'
                state = address.state if address else 'CA'  # Default to 'CA' if not provided
                zip_code = address.zip_code if address else 'N/A'

                # Format data for CSV
                formatted_data = (
                    f"I;{last_name};{first_name};;{gender};{formatted_date_of_birth};"
                    f"{team_abbr};{team_name};;;{parent_name};"
                    f"{street_address};{city};{state};{zip_code};USA;"
                    f"{phone};;;;;;;{email}"
                )
                writer.writerow([formatted_data])

            # Reset the file pointer to the beginning
            output.seek(0)

            # Return the CSV file as a download
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={"Content-disposition": "attachment; filename=athletes_parents.csv"}
            )

        except Exception as e:
            logging.exception("Unexpected error occurred")
            return {'error': 'Internal server error'}, 500

        finally:
            # Ensure the session is closed
            session.close()
