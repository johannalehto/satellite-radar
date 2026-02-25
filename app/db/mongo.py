from pymongo import MongoClient

from app.config import MONGO_URI
from app.satellite_catalog.repository import SatelliteCatalogRepository


def create_satellite_catalog_repository() -> SatelliteCatalogRepository:
    client = MongoClient(MONGO_URI)
    db = client["satellites_db"]
    collection = db["satellite_catalog"]
    return SatelliteCatalogRepository(collection=collection)
