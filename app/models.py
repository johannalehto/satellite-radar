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


class RawTLEEntry(BaseModel):
    name: str
    line1: str
    line2: str


class CelestrakSatelliteOutput(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData | None = None


class SatelliteTLEUpdate(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData


class SatelliteCatalogItem(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData | None = None
