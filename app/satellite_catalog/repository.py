from datetime import datetime
from typing import Any

from pymongo import UpdateOne

from app.models import SatelliteTLEUpdate


class SatelliteCatalogRepository:
    def __init__(self, collection):
        self.collection = collection

    def upsert_tles_to_db(self, tle_updates: list[SatelliteTLEUpdate]) -> None:
        operations = [
            UpdateOne(
                {"satellite_id": item.satellite_id},
                {
                    "$set": {
                        "satellite_id": item.satellite_id,
                        "satellite_name": item.satellite_name,
                        "tle": item.tle.model_dump(),
                    }
                },
                upsert=True,
            )
            for item in tle_updates
        ]

        if not operations:
            return

        result = self.collection.bulk_write(operations)
        print(
            f"Matched {result.matched_count}, "
            f"modified {result.modified_count}, "
            f"upserted {result.upserted_count} "
            "satellite TLE documents into MongoDB"
        )

    def get_satellite_data_from_db(
        self, lat: float, lon: float, timestamp: datetime
    ) -> list[dict[str, Any]]:
        """retrieves satellites above a certain lat/lon at a given timestamp."""
        # query = {
        #     "latitude": {"$gte": lat - 0.5, "$lte": lat + 0.5},
        #     "longitude": {"$gte": lon - 0.5, "$lte": lon + 0.5},
        #     "timestamp": timestamp,
        # }
        # return list(self.collection.find(query))

        """
        Placeholder until implementing the real query against next_positions[].
        For now returns any satellites (limited) so the endpoint works end-to-end.
        """
        return list(
            self.collection.find(
                {},
                projection={"_id": 0, "satellite_id": 1, "satellite_name": 1},
            ).limit(10)
        )
