from typing import Protocol

from fastapi import APIRouter, HTTPException
from starlette import status

from app.models import SatelliteCatalogStatus


class SatelliteCatalogServiceProtocol(Protocol):
    def get_catalog_status(self) -> SatelliteCatalogStatus: ...


def create_satellite_catalog_router(service: SatelliteCatalogServiceProtocol) -> APIRouter:
    router = APIRouter()

    @router.get("/satellite_catalog/status")
    async def get_catalog_status() -> SatelliteCatalogStatus:
        try:
            return service.get_catalog_status()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not retrieve satellite catalog status",
            ) from e

    return router
