import os

from pymongo import MongoClient


def load_secret(file_path):
    try:
        with open(file_path) as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


MONGO_PASSWORD = load_secret("/run/secrets/mongo_password") or os.getenv("MONGO_PASSWORD")

MONGO_URL = f"mongodb+srv://johanna:{
    MONGO_PASSWORD}@cluster0.afeh5pj.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(MONGO_URL)

try:
    print(client.list_database_names())
    print("Connection successful!")
except Exception as e:
    print(f"Error: {e}")
