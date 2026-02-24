from datetime import datetime

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
        self.repository = repository or SatelliteCatalogRepository()

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
    def _satellite_data_to_satellites_now(satellite_data) -> SatellitesNowResponse:
        return SatellitesNowResponse(
            location=(satellite_data[0].latitude, satellite_data[0].longitude),
            satellites=[
                Satellite(id=satellite["satellite_id"], name=satellite["satellite_name"])
                for satellite in satellite_data
            ],
        )

    def get_satellites_from_catalog(
        self, lat: float, lon: float, now: datetime
    ) -> SatellitesNowResponse | None:

        try:
            satellites_now_from_db = self.repository.get_satellite_data_from_db(lat, lon, now)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        return self._satellite_data_to_satellites_now(satellites_now_from_db)
