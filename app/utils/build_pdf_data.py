from datetime import datetime
from app.constants import constants
from app.models import Athlete
from app.utils.CalculateAge import calculate_age
from app.utils.CalculateAge import calculate_age_in_year
from app.utils.CalculateDivision import calculate_division


class BuildPDFData:
    def __init__(self, **form_data):
        # Directly store parent info and athletes list
        self.parent_info = {key: value for key, value in form_data.items() if key != 'athletes'}
        self._athletes_data = form_data.get('athletes', [])

    @property
    def athletes_data(self):
        return self._athletes_data

    def get_player_contract_form_data(self, athlete: Athlete) -> dict:
        athlete_full_name = ' '.join([athlete.first_name, athlete.last_name])
        athlete_age = calculate_age(athlete.date_of_birth)
        athlete_age_in_year = calculate_age_in_year(athlete.date_of_birth)
        athlete_division = calculate_division(athlete_age_in_year)

        return {
            'KidSig': athlete_full_name,
            'Year': '24',  # TODO: Make this dynamic and not hardcoded
            'TeamName': 'Antelope Valley Track Club',
            'TrackFieldBox': 'Yes',
            'Boy': 'X' if athlete.gender == 'male' else ' ',
            'Girl': ' ' if athlete.gender == 'male' else 'X',
            'Age': athlete_age,
            'Division': athlete_division,
            'PlayersName': athlete_full_name,
            'Date of Birth': athlete.date_of_birth.strftime('%m/%d/%Y'),
            'Age_2': athlete,
            'DateSigned': datetime.now().strftime('%m/%d/%Y'),
            'PlayersAddress': self.parent_info['streetAddress'],
            'CityZip': f"{self.parent_info['city']}  {self.parent_info['zipcode']}",
            'Phone': self.parent_info['phoneNumber'],
            'Email': self.parent_info['email'],
            'Cell PhoneEmergency': self.parent_info['emergencyPhone'],
            'Contact': self.parent_info['emergencyName'],
            'Carrier': self.parent_info['carrier'],
            'Policy Number': self.parent_info['policyNumber'],
            'PlayerName2': " " * 40 + ' '.join([athlete.first_name, athlete.last_name]),
            'Name_Parent_or_Guardian_print[0]': " " * 20 + self.parent_info['parentName'],
            'NameOfParent': self.parent_info['parentName'],
        }

    def get_code_of_conduct_form_data(self, athlete: Athlete,
                                      medical_conditions: str = '',
                                      last_physical: str = '') -> dict:
        # Similar to get_player_contract_form_data, but for the code of conduct form
        athlete_full_name = ' '.join([athlete.first_name, athlete.last_name])
        return {
            'PLAYER': athlete_full_name,
            'CLUB': constants.TRACK_CLUB_NAME,
            'My Child 1': athlete_full_name,
            'My Child 2': medical_conditions,  # TODO: Rename this field on the pdf, it's the medical conditions field
            'DATED': last_physical,
            'Player Name Please Print': athlete_full_name,
            'Parents Name Please Print': self.parent_info['parentName'],
            'CoachClub Officials Name Please Print': 'Tameisha Warner',
        }
