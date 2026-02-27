from fastapi import FastAPI

from app.satellite_catalog.service import SatelliteCatalogService
from app.satellite_radar.router import create_satellite_radar_router
from app.satellite_radar.service import SatelliteRadarService


def create_app() -> FastAPI:
    app = FastAPI()

    catalog_service = SatelliteCatalogService()
    radar_service = SatelliteRadarService(satellite_catalog=catalog_service)
    app.include_router(create_satellite_radar_router(service=radar_service))

    return app


app = create_app()
