def calculate_division(age):
    division = ''
    if 5 <= age <= 8:
        division = 'Gremlins Age 5-8'
    elif 9 <= age <= 10:
        division = 'Bantam Age 9-10'
    elif 11 <= age <= 12:
        division = 'Midget Age 11-12'
    elif 13 <= age <= 14:
        division = 'Youth Age 13-14'
    elif 15 <= age <= 16:
        division = 'Intermediate Age 15-16'
    elif 17 <= age <= 18:
        division = 'Young Age 17-18'

    return division
