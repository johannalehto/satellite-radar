from pymongo import MongoClient, UpdateOne

from app.config import MONGO_URI
from app.models import SatellitePosition

client = MongoClient(MONGO_URI)
db = client["satellites_db"]
collection = db["satellite_catalog"]


class SatelliteCatalogRepository:
    @staticmethod
    def upsert_positions_to_db(positions: list[SatellitePosition]) -> None:
        """
        inserts a list of SatellitePosition data into MongoDB.
        """
        operations = [
            UpdateOne(
                {"satellite_id": position.satellite_id},
                {"$set": position.model_dump()},
                upsert=True,
            )
            for position in positions
        ]
        result = collection.bulk_write(operations)
        print(
            f"Matched {result.matched_count}, "
            f"modified {result.modified_count}, "
            f"upserted {result.upserted_count} "
            "satellite positions into MongoDB"
        )

    @staticmethod
    def get_satellite_data_from_db(lat, lon, timestamp):
        """retrieves satellites above a certain lat/lon at a given timestamp."""
        query = {
            "latitude": {"$gte": lat - 0.5, "$lte": lat + 0.5},
            "longitude": {"$gte": lon - 0.5, "$lte": lon + 0.5},
            "timestamp": timestamp,
        }
        return list(collection.find(query))
