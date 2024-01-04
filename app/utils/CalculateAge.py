from datetime import date


def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def calculate_age_in_year(birth_date):
    today = date.today()
    age = today.year - birth_date.year

    return age
