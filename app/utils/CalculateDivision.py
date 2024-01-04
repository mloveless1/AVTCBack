def calculate_division(age):
    division = ''
    if 5 <= age <= 8:
        division = 'Gremlins'
    elif 9 <= age <= 10:
        division = 'Bantam'
    elif 11 <= age <= 12:
        division = 'Juniors'
    elif 13 <= age <= 14:
        division = 'Youth'
    elif 15 <= age <= 16:
        division = 'Intermediate'
    elif 17 <= age <= 18:
        division = 'Young Age'

    return division
