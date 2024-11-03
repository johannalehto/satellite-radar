import os
from pymongo import MongoClient

def load_secret(file_path):
    try:
        with open(file_path) as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


MONGO_USERNAME = load_secret("/run/secrets/mongo_username") or os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = load_secret("/run/secrets/mongo_password") or os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "cluster0.afeh5pj.mongodb.net")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "satellites_db")

MONGO_URL = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DBNAME}?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client[MONGO_DBNAME]
