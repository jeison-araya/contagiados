import pymongo
from decouple import config

URI = config('MONGO_URI')
client = pymongo.MongoClient(URI)
db = None

def get_db():
    """Get the database connection.
    Returns:
        database: Database connection instance.
    """
    global db
    
    if db is None:
        db = client.if5000_project_2021
    return db