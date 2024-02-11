import datetime


class BuildPDFForm:
    def __init__(self, **form_data):
        # Directly store parent info and athletes list
        self.parent_info = {key: value for key, value in form_data.items() if key != 'athletes'}
        self._athletes_data = form_data.get('athletes', [])

    @property
    def athletes_data(self):
        return self._athletes_data

    def get_player_contract_form_data(self, athlete):
        # Assuming 'athlete' is a dictionary containing athlete-specific data
        # Calculate athlete's age and division here or ensure they are included in 'athlete' data
        return {
            'KidSig': athlete['full_name'],
            'Year': '24',
            'TeamName': 'Antelope Valley Track Club',
            'TrackFieldBox': 'Yes',
            'Boy': 'X' if athlete['gender'] == 'male' else ' ',
            'Girl': ' ' if athlete['gender'] == 'male' else 'X',
            'Age': str(athlete['age']),  # Ensure 'age' is calculated beforehand or provided
            'Division': athlete['division'],  # Ensure 'division' is calculated or provided
            'PlayersName': athlete['full_name'],
            'Date of Birth': athlete['dateOfBirth'].strftime('%m/%d/%Y'),
            'Age_2': str(athlete['age']),  # Duplicate of 'Age', adjust if necessary
            'DateSigned': datetime.now().strftime('%m/%d/%Y'),
            'PlayersAddress': self.parent_info['streetAddress'],
            'CityZip': f"{self.parent_info['city']}  {self.parent_info['zipcode']}",
            'Phone': self.parent_info['phoneNumber'],
            'Email': self.parent_info['email'],
            'Cell PhoneEmergency': self.parent_info['emergencyPhone'],
            'Contact': self.parent_info['emergencyName'],
            'Carrier': self.parent_info['carrier'],
            'Policy Number': self.parent_info['policyNumber'],
            'PlayerName2': " " * 40 + athlete['full_name'],  # Adjust spacing as needed
            'Name_Parent_or_Guardian_print[0]': " " * 20 + self.parent_info['parentName'],
            'NameOfParent': self.parent_info['parentName'],
        }

    def get_code_of_conduct_form_data(self, athlete):
        # Similar to get_player_contract_form_data, but for the code of conduct form
        return {
                'PLAYER': athlete.full_name,
                'CLUB': 'Antelope Valley Track Club',
                'My Child 1': athlete.full_name,
                'My Child 2': athlete['medicalConditions'],
                'DATED': athlete['lastPhysical'],
                'Player Name Please Print': athlete.full_name,
                'Parents Name Please Print': athlete['parentName'],
                'CoachClub Officials Name Please Print': 'Tameisha Warner',
            }
