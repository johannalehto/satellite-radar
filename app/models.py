from datetime import datetime

from pydantic import BaseModel


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
    tle: TLEData


class SatelliteTLEUpdate(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData


class SatelliteCatalogItem(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData


"""
RADAR MODELS
"""


class RadarTrackPoint(BaseModel):
    timestamp: datetime
    azimuth_deg: float
    elevation_deg: float
    distance_km: float


class RadarSatelliteResult(BaseModel):
    satellite_id: str
    satellite_name: str
    visible_from: datetime
    visible_until: datetime
    max_elevation_deg: float
    start_azimuth_deg: float
    start_direction: str
    end_azimuth_deg: float
    end_direction: str
    track: list[RadarTrackPoint]
