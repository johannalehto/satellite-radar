from fastapi import APIRouter, HTTPException

from app.models import SatellitesAboveResponse
from app.satellite_radar.service import SatelliteRadarService


def create_satellite_radar_router(service: SatelliteRadarService) -> APIRouter:
    router = APIRouter()

    @router.get("/satellite_radar/get_satellites_above/{lat}/{lon}")
    async def get_satellites_above(lat: float, lon: float) -> SatellitesAboveResponse:
        try:
            return service.get_satellites_now(lat, lon)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    return router
