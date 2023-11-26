from pymongo import MongoClient

# Connect to MongoDB and define collections
client = MongoClient('localhost', 27017)
db = client.AVTrackClub
athletes_collection = db.athletes
parents_collection = db.parents
events_collections = db.events