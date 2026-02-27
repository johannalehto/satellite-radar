from fastapi import APIRouter

from app.models import SatellitesAboveResponse
from app.satellite_radar.service import SatelliteRadarService

router = APIRouter()


@router.get("/satellite_radar/get_satellites_above/{lat}/{lon}")
async def get_satellites_above(lat: float, lon: float) -> SatellitesAboveResponse | None:
    service = SatelliteRadarService()
    try:
        satellites_above = service.get_satellites_above(lat, lon)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return satellites_above
