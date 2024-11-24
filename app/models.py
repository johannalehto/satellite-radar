from datetime import datetime

from pydantic import BaseModel


class Satellite(BaseModel):
    id: int
    name: str


class SatellitesNowResponse(BaseModel):
    location: tuple[float, float]
    satellites: list[Satellite]


class Position(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    altitude_km: float


class CelestrakSatelliteOutput(BaseModel):
    satellite_id: str
    satellite_name: str
    next_positions: list[Position]


class SatellitePosition(BaseModel):
    satellite_id: str
    satellite_name: str
    next_positions: list[Position]
