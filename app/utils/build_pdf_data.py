from datetime import datetime
from app.constants import constants
from app.utils.CalculateAge import calculate_age, calculate_age_in_year
from app.utils.CalculateDivision import calculate_division


class BuildPDFData:
    def __init__(self, **form_data):
        # Store parent info and athletes list directly from the request JSON
        self.parent_info = {key: value for key, value in form_data.items() if key != 'athletes'}
        self._athletes_data = form_data.get('athletes', [])

    @property
    def athletes_data(self):
        return self._athletes_data

    def get_player_contract_form_data(self, athlete_data: dict, season_year) -> dict:
        """Generates the data required for the Player Contract PDF."""
        parent_full_name = ' '.join([self.parent_info['parentFirstName'], self.parent_info['parentLastName']])
        athlete_full_name = ' '.join([athlete_data['athleteFirstName'], athlete_data['athleteLastName']])
        athlete_date_of_birth = datetime.strptime(athlete_data['dateOfBirth'], '%Y-%m-%d').date()
        athlete_age = str(calculate_age(athlete_date_of_birth))
        athlete_age_in_year = calculate_age_in_year(athlete_date_of_birth, season_year)
        athlete_division = calculate_division(athlete_age_in_year)

        return {
            'KidSig': ' ',
            'Year': '25',  # TODO: Make this dynamic and not hardcoded
            'TeamName': 'Antelope Valley Track Club',
            'TrackFieldBox': 'Yes',
            'Boy': 'X' if athlete_data['gender'] == 'male' else ' ',
            'Girl': ' ' if athlete_data['gender'] == 'male' else 'X',
            'Age': athlete_age,
            'Division': athlete_division,
            'PlayersName': athlete_full_name,
            'Date of Birth': datetime.strptime(athlete_data['dateOfBirth'], '%Y-%m-%d').strftime('%m/%d/%Y'),
            'Age_2': athlete_age,
            'DateSigned': datetime.now().strftime('%m/%d/%Y'),
            'PlayersAddress': self.parent_info['streetAddress'],
            'CityZip': f"{self.parent_info['city']} {self.parent_info['zipcode']}",
            'Phone': self.parent_info['phoneNumber'],
            'Email': self.parent_info['email'],
            'Cell PhoneEmergency': self.parent_info['emergencyPhone'],
            'Contact': self.parent_info['emergencyName'],
            'Carrier': self.parent_info['carrier'],
            'Policy Number': self.parent_info['policyNumber'],
            'PlayerName2': " " * 40 + athlete_full_name,
            'Name_Parent_or_Guardian_print[0]': " " * 20 + parent_full_name,
            'NameOfParent': parent_full_name,
        }

    def get_code_of_conduct_form_data(self, athlete_data: dict) -> dict:
        """Generates the data required for the Code of Conduct PDF."""
        parent_full_name = ' '.join([self.parent_info['parentFirstName'], self.parent_info['parentLastName']])
        athlete_full_name = ' '.join([athlete_data['athleteFirstName'], athlete_data['athleteLastName']])

        return {
            'PLAYER': athlete_full_name,
            'CLUB': constants.TRACK_CLUB_NAME,
            'My Child 1': athlete_full_name,
            'My Child 2': athlete_data.get('medicalConditions', ''),  # Medical conditions
            'DATED': athlete_data.get('lastPhysical', ''),  # Date of last physical
            'Player Name Please Print': athlete_full_name,
            'Parents Name Please Print': parent_full_name,
            'CoachClub Officials Name Please Print': 'Tameisha Warner',
        }
