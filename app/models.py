from datetime import datetime

from pydantic import BaseModel


class Satellite(BaseModel):
    id: int
    name: str


class SatellitesNowResponse(BaseModel):
    location: tuple[float, float]
    satellites: list[Satellite]


class SatellitesAboveResponse(BaseModel):
    location: tuple[float, float]
    satellites: list[Satellite]


class Position(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    altitude_km: float


class TLEParsed(BaseModel):
    epoch: datetime
    inclination_deg: float
    raan_deg: float
    eccentricity: float
    mean_motion_rev_per_day: float
    drag_term_bstar: float


class TLEData(BaseModel):
    line1: str
    line2: str
    group: str
    source: str
    fetched_at: datetime
    parsed: TLEParsed


class CelestrakSatelliteOutput(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData | None = None
    next_positions: list[Position] | None = None  # TODO: to be deprecated
    fetched_at: datetime  # TODO: to be deprecated


class SatelliteTLEUpdate(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData


class SatelliteCatalogItem(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData | None = None
    next_positions: list[Position] | None = None  # TODO: to be deprecated
    fetched_at: datetime  # TODO: to be deprecated


class SatellitePosition(BaseModel):
    satellite_id: str
    satellite_name: str
    next_positions: list[Position]
    fetched_at: datetime
