from datetime import UTC, datetime

from app.models import SatellitesAboveResponse, SatellitesNowResponse
from app.satellite_catalog.service import SatelliteCatalogService


def build_satellites_above_response(
    satellites_now: SatellitesNowResponse,
    *,
    limit: int = 10,
) -> SatellitesAboveResponse:
    return SatellitesAboveResponse(
        location=satellites_now.location,
        satellites=satellites_now.satellites[:limit],
    )


class SatelliteRadarService:
    def __init__(self, satellite_catalog: SatelliteCatalogService):
        self.satellite_catalog = satellite_catalog

    def get_satellites_now(
        self,
        lat: float,
        lon: float,
        *,
        limit: int = 10,
        now: datetime | None = None,
    ) -> SatellitesAboveResponse:
        # Use UTC to match Mongo ISODate values.
        now = now or datetime.now(UTC)

        satellites_now = self.satellite_catalog.get_satellites_from_catalog(lat, lon, now)
        return build_satellites_above_response(satellites_now, limit=limit)
