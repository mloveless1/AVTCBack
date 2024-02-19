import os
import io
import csv
from datetime import datetime
from flask import Response
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Athlete, Parent
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()


# noinspection PyMethodMayBeStatic
class PullerResource(Resource):

    @jwt_required()
    def get(self):
        # Load database URI from environment variable
        database_uri = os.getenv('DATABASE_URL')

        # Create a database engine
        engine = create_engine(database_uri)

        # Create a session
        session = Session(bind=engine)

        try:
            # Perform a JOIN query between Athletes and Parents
            # noinspection PyTypeChecker
            query = session.query(Athlete, Parent).join(Parent, Athlete.parent_id == Parent.parent_id)
            results = query.all()

            # Create a CSV in memory
            output = io.StringIO()
            writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

            team_abbr = "AVTC"
            team_name = "ANTELOPE VALLEY TRACK CLUB"

            for athlete, parent in results:

                athlete_name_tokens = athlete.full_name.split()
                first_name, last_name= str(athlete_name_tokens[0]).capitalize().strip(), str(athlete_name_tokens[1])

                suffix = ''
                if len(athlete_name_tokens) == 3:
                    suffix = ' ' + str(athlete_name_tokens[2])

                last_name = (last_name + suffix).title().strip()

                gender = athlete.gender
                if athlete.gender == 'male':
                    gender = 'M'
                elif athlete.gender == 'female':
                    gender = 'F'

                # Convert date_of_birth to mm/dd/yyyy format
                date_of_birth_obj = datetime.strptime(str(athlete.date_of_birth), '%Y-%m-%d')
                formatted_date_of_birth = date_of_birth_obj.strftime('%m/%d/%Y')

                parent_name = str(parent.parent_name).replace('  ', ' ').strip().title()
                email = str(parent.email).strip()
                phone = str(parent.phone_number).strip()

                # Format data as per the provided structure
                formatted_data = (f"I;{last_name};{first_name};;"
                                  f"{gender};{formatted_date_of_birth};{team_abbr};"
                                  f"{team_name};;;{parent_name.title()};"
                                  f"STREETADDRESS;CITY;STATE;"
                                  f"ZIP;COUNTRY;"
                                  f"{phone};;;;;;;{email}")
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
            # Handle exceptions
            return {'error': str(e)}, 500

        finally:
            # Close the session
            session.close()
