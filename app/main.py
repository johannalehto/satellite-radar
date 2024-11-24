from fastapi import FastAPI

from app.satellite_radar.router import router as satellite_radar_router

app = FastAPI()

app.include_router(satellite_radar_router)
