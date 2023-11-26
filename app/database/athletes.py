from app.database import athletes_collection

"""
Athlete:
Id
Full Name: String
Date of Birth: Date
Parent: Id number of the parent
Uniform Sizes: List [youth small, youth medium, youth large, s, m, l, xl]
Balance: Float
"""


# CRUD for athletes collection
def create_athlete(data):
    """Create a new athlete and return the inserted athlete."""
    athlete_id = athletes_collection.insert_one(data).inserted_id
    return get_athlete_by_id(athlete_id)


def get_all_athletes():
    """Return all athletes."""
    return list(athletes_collection.find({}))


def get_athlete_by_id(athlete_id):
    """Return a specific athlete by ID."""
    return athletes_collection.find_one({"_id": athlete_id})


def update_athlete(athlete_id, data):
    """Update an athlete and return the updated athlete."""
    athletes_collection.update_one({"_id": athlete_id}, {"$set": data})
    return get_athlete_by_id(athlete_id)


def delete_athlete(athlete_id):
    """Delete an athlete by ID."""
    athletes_collection.delete_one({"_id": athlete_id})
    return {"message": "Athlete record deleted successfully"}