from datetime import datetime
from typing import Any

from app.db.mongo import create_satellite_catalog_repository
from app.models import (
    CelestrakSatelliteOutput,
    Satellite,
    SatellitesNowResponse,
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
        self.celestrak_service = celestrak_service or CelestrakService()
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
        celestrak_outputs = self.celestrak_service.fetch_tles()
        tle_updates = self._to_tle_updates(celestrak_outputs)
        self.repository.upsert_tles_to_db(tle_updates)

    @staticmethod
    def _satellite_data_to_satellites_now(
        satellite_data: list[dict[str, Any]],
        lat: float,
        lon: float,
    ) -> SatellitesNowResponse:
        return SatellitesNowResponse(
            location=(lat, lon),
            satellites=[
                Satellite(id=satellite["satellite_id"], name=satellite["satellite_name"])
                for satellite in satellite_data
            ],
        )

    def get_satellites_from_catalog(
        self, lat: float, lon: float, now: datetime
    ) -> SatellitesNowResponse:
        satellite_data = self.repository.get_satellite_data_from_db(lat, lon, now)

        if not satellite_data:
            return SatellitesNowResponse(location=(lat, lon), satellites=[])
            # TODO: return error or exception. empty list for now.

        return self._satellite_data_to_satellites_now(satellite_data, lat, lon)
