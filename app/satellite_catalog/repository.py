from datetime import datetime
from typing import Any

from pymongo import UpdateOne

from app.models import SatellitePosition


class SatelliteCatalogRepository:
    def __init__(self, collection):
        self.collection = collection

    def upsert_positions_to_db(self, positions: list[SatellitePosition]) -> None:
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
        result = self.collection.bulk_write(operations)
        print(
            f"Matched {result.matched_count}, "
            f"modified {result.modified_count}, "
            f"upserted {result.upserted_count} "
            "satellite positions into MongoDB"
        )

    def get_satellite_data_from_db(
        self, lat: float, lon: float, timestamp: datetime
    ) -> list[dict[str, Any]]:
        """retrieves satellites above a certain lat/lon at a given timestamp."""
        query = {
            "latitude": {"$gte": lat - 0.5, "$lte": lat + 0.5},
            "longitude": {"$gte": lon - 0.5, "$lte": lon + 0.5},
            "timestamp": timestamp,
        }
        return list(self.collection.find(query))
