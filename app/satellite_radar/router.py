from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from starlette import status

from app.models import SatelliteRadarItem
from app.satellite_radar.errors import (
    SatelliteRadarCatalogUnavailableError,
    SatelliteRadarInvalidArgumentError,
    SatelliteRadarServiceError,
)
from app.satellite_radar.service import SatelliteRadarService


def create_satellite_radar_router(service: SatelliteRadarService) -> APIRouter:
    router = APIRouter()

    @router.get("/satellite_radar/get_visible_satellites/{lat}/{lon}")
    async def get_visible_satellites(
        lat: Annotated[float, Path(ge=-90, le=90)],
        lon: Annotated[float, Path(ge=-180, le=180)],
    ) -> list[SatelliteRadarItem]:
        try:
            return service.get_visible_satellites(
                lat=lat,
                lon=lon,
            )
        except SatelliteRadarInvalidArgumentError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e
        except SatelliteRadarCatalogUnavailableError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e),
            ) from e
        except SatelliteRadarServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            ) from e

    return router
