from app.db.mongo import create_satellite_catalog_repository
from app.models import (
    CelestrakSatelliteOutput,
    SatelliteCatalogItem,
    SatelliteTLEUpdate,
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

    @staticmethod
    def _to_tle_updates(
        outputs: list[CelestrakSatelliteOutput],
    ) -> list[SatelliteTLEUpdate]:
        return [
            SatelliteTLEUpdate(
                satellite_id=output.satellite_id,
                satellite_name=output.satellite_name,
                tle=output.tle,
            )
            for output in outputs
            if output.tle is not None
        ]

    def update_satellite_catalog_with_tle_data(self) -> None:
        celestrak_service = self.celestrak_service or CelestrakService()
        celestrak_outputs = celestrak_service.fetch_tles()

        tle_updates = self._to_tle_updates(celestrak_outputs)
        self.repository.upsert_tles_to_db(tle_updates)

    def get_all_satellites(self, *, limit: int | None = None) -> list[SatelliteCatalogItem]:
        return self.repository.get_all_satellites(limit=limit)
