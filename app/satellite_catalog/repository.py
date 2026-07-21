from pymongo import DESCENDING, UpdateOne

from app.models import SatelliteCatalogItem, SatelliteCatalogStatus, SatelliteTLEUpdate


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

    def get_catalog_status(self) -> SatelliteCatalogStatus:
        satellite_count = self.collection.count_documents({})
        latest_doc = self.collection.find_one(
            {},
            projection={
                "_id": 0,
                "tle.fetched_at": 1,
                "tle.source": 1,
            },
            sort=[("tle.fetched_at", DESCENDING)],
        )

        latest_tle = (latest_doc or {}).get("tle", {})

        return SatelliteCatalogStatus(
            satellite_count=satellite_count,
            latest_tle_fetched_at=latest_tle.get("fetched_at"),
            source=latest_tle.get("source"),
        )
