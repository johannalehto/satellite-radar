from pymongo import MongoClient

from app.config import MONGO_PASSWORD

MONGO_URL = (
    f"mongodb+srv://johanna:{MONGO_PASSWORD}@cluster0.afeh5pj.mongodb.net/"
    "?retryWrites=true&w=majority"
)
client = MongoClient(MONGO_URL)
print(client.list_database_names())
