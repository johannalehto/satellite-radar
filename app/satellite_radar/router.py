from fastapi import APIRouter, HTTPException

from app.models import SatelliteRadarItem
from app.satellite_radar.service import SatelliteRadarService


def create_satellite_radar_router(service: SatelliteRadarService) -> APIRouter:
    router = APIRouter()

    @router.get("/satellite_radar/get_visible_satellites/{lat}/{lon}")
    async def get_visible_satellites(lat: float, lon: float) -> list[SatelliteRadarItem]:
        try:
            return service.get_visible_satellites(
                lat=lat,
                lon=lon,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    return router
