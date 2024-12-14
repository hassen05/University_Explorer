import pymongo

def get_database():
    """
    Connect to MongoDB and return the database object.
    """
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["university_data"]
    return db

def get_collection(collection_name):
    """
    Return a specific collection from the database.
    """
    db = get_database()
    return db[collection_name]
