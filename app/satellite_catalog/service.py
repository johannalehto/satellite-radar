from app.db.mongo import create_satellite_catalog_repository
from app.models import (
    SatelliteCatalogItem,
    SatelliteCatalogStatus,
)
from app.satellite_catalog.celestrak_service import CelestrakService
from app.satellite_catalog.repository import SatelliteCatalogRepository


class SatelliteCatalogService:
    def __init__(
        self,
        celestrak_service: CelestrakService | None = None,
        repository: SatelliteCatalogRepository | None = None,
    ):
        self.celestrak_service = celestrak_service
        self.repository = repository or create_satellite_catalog_repository()

    def update_satellite_catalog_with_tle_data(self) -> None:
        celestrak_service = self.celestrak_service or CelestrakService()
        tle_updates = celestrak_service.fetch_tles()

        self.repository.upsert_tles_to_db(tle_updates)

    def update_satellite_catalog_with_metadata(self) -> None:
        celestrak_service = self.celestrak_service or CelestrakService()
        metadata_updates = celestrak_service.fetch_satcat_metadata()

        self.repository.update_metadata_in_db(metadata_updates)

    def get_all_satellites(self, *, limit: int | None = None) -> list[SatelliteCatalogItem]:
        return self.repository.get_all_satellites(limit=limit)

    def get_catalog_status(self) -> SatelliteCatalogStatus:
        return self.repository.get_catalog_status()
