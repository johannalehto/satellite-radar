from pymongo import UpdateOne

from app.models import SatelliteCatalogItem, SatelliteTLEUpdate


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

    def get_all_satellites(self, *, limit: int | None = None) -> list[SatelliteCatalogItem]:
        cursor = self.collection.find(
            {},
            projection={
                "_id": 0,
                "satellite_id": 1,
                "satellite_name": 1,
                "tle": 1,
            },
        )

        if limit is not None:
            cursor = cursor.limit(limit)

        return [SatelliteCatalogItem.model_validate(doc) for doc in cursor]
