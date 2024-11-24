from datetime import datetime

from app.models import SatellitesNowResponse
from app.satellite_catalog.service import get_satellites_from_catalog

def build_satellites_list(satellites: list) -> list:
    return [
        {
            "id": sat["satid"],
            "name": sat["satname"],
        }
        for sat in satellites
    ]


def build_satellites_now_response(satellites_now: dict) -> SatellitesNowResponse:

    response = SatellitesNowResponse(
        location=satellites_now.location,
        satellites=build_satellites_list(satellites_now.satellites)[:5],

    )

    return response


class SatelliteRadarService:
    def __init__(self):
        pass

    def get_satellites_above(self, lat: float, lon: float) -> SatellitesNowResponse | None:

        now = datetime.now()

        try:
            satellites_now = get_satellites_from_catalog(lat, lon, now)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        return build_satellites_now_response(satellites_now)


