from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.health import create_health_router
from app.satellite_catalog.router import create_satellite_catalog_router
from app.satellite_catalog.service import SatelliteCatalogService
from app.satellite_radar.router import create_satellite_radar_router
from app.satellite_radar.service import SatelliteRadarService


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://satellites-debug-ui.fly.dev",
            "http://localhost:5173",  # Vite default ports
            "http://127.0.0.1:5173",
            "https://satellite-radar-web.fly.dev",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    catalog_service = SatelliteCatalogService()
    radar_service = SatelliteRadarService(satellite_catalog=catalog_service)
    app.include_router(create_health_router())
    app.include_router(create_satellite_catalog_router(service=catalog_service))
    app.include_router(create_satellite_radar_router(service=radar_service))

    return app


app = create_app()
