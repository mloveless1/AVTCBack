import os
import io
import csv
from flask import Response
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Athlete, Parent
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()


# noinspection PyMethodMayBeStatic
class PullerResource(Resource):
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
            writer = csv.writer(output, delimiter=';')

            team_abbr = "V"
            team_name = "ANTELOPE VALLEY"

            for athlete, parent in results:

                athlete_name_tokens = athlete.full_name.split()
                first_name, last_name = athlete_name_tokens[0], athlete_name_tokens[1]

                gender = athlete.gender
                if athlete.gender == 'male':
                    gender = 'B'
                elif athlete.gender == 'female':
                    gender = 'G'

                # Format data as per the provided structure
                formatted_data = (f"I;{last_name};{first_name};"
                                  f"{gender};{team_abbr};"
                                  f"{team_name};{parent.parent_name}"
                                  f";{parent.phone_number};{parent.phone_number};;;;;;;")
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
