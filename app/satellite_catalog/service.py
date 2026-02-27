from datetime import datetime
from typing import Any

from app.db.mongo import create_satellite_catalog_repository
from app.models import Satellite, SatellitePosition, SatellitesNowResponse
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

    def update_satellite_catalog(self) -> None:
        satellite_positions = self.celestrak_service.calculate_positions()

        position_data = [
            SatellitePosition(
                satellite_id=output.satellite_id,
                satellite_name=output.satellite_name,
                next_positions=output.next_positions,
                fetched_at=output.fetched_at,
            )
            for output in satellite_positions
        ]

        self.repository.upsert_positions_to_db(position_data)

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
