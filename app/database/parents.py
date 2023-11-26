from app.database import parents_collection

"""
Parent:
Id
Full Name: String
Phone Number: String
Email: String
Volunteer days: List of dates
"""


# CRUD for parent collection
def create_parent(data):
    """Create a new parent and return the inserted parent."""
    parent_id = parents_collection.insert_one(data).inserted_id
    return get_parent_by_id(parent_id)


def get_all_parents():
    """Return all parents."""
    return list(parents_collection.find({}))


def get_parent_by_id(parent_id):
    """Return a specific parent by ID."""
    return parents_collection.find_one({"_id": parent_id})


def update_parent(parent_id, data):
    """Update a parent and return the updated parent."""
    parents_collection.update_one({"_id": parent_id}, {"$set": data})
    return get_parent_by_id(parent_id)


def delete_parent(parent_id):
    """Delete a parent by ID."""
    parents_collection.delete_one({"_id": parent_id})
    return {"message": "Parent record deleted successfully"}