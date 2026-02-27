from datetime import datetime

from app.models import SatellitesAboveResponse, SatellitesNowResponse
from app.satellite_catalog.service import SatelliteCatalogService


def build_satellites_above_response(
    satellites_now: SatellitesNowResponse,
) -> SatellitesAboveResponse:

    response = SatellitesAboveResponse(
        location=satellites_now.location,
        satellites=satellites_now.satellites[:5],
    )

    return response


class SatelliteRadarService:
    def __init__(self):
        self.satellite_catalog = SatelliteCatalogService()

    def get_satellites_above(self, lat: float, lon: float) -> SatellitesAboveResponse | None:

        now = datetime.now()

        try:
            satellites_now = self.satellite_catalog.get_satellites_from_catalog(lat, lon, now)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        return build_satellites_above_response(satellites_now)
