from __future__ import annotations

from datetime import date as Date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


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


class RawSatcatEntry(BaseModel):
    satellite_id: int = Field(alias="NORAD_CAT_ID")
    satellite_name: str = Field(alias="OBJECT_NAME")
    owner: str | None = Field(default=None, alias="OWNER")
    object_type: str | None = Field(default=None, alias="OBJECT_TYPE")
    launch_date: str | None = Field(default=None, alias="LAUNCH_DATE")
    launch_site: str | None = Field(default=None, alias="LAUNCH_SITE")


class SatelliteTLEUpdate(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData


class SatelliteObjectType(StrEnum):
    PAYLOAD = "payload"
    ROCKET_BODY = "rocket_body"
    DEBRIS = "debris"
    UNKNOWN = "unknown"


class SatelliteOwner(BaseModel):
    code: str
    name: str


class SatelliteLaunchSite(BaseModel):
    code: str
    name: str


class SatelliteLaunch(BaseModel):
    date: Date | None = None
    site: SatelliteLaunchSite | None = None


class SatelliteMetadata(BaseModel):
    source: str
    fetched_at: datetime
    owner: SatelliteOwner | None = None
    object_type: SatelliteObjectType | None = None
    launch: SatelliteLaunch | None = None


class SatelliteMetadataUpdate(BaseModel):
    satellite_id: str
    satellite_name: str
    metadata: SatelliteMetadata


class SatelliteCatalogItem(BaseModel):
    satellite_id: str
    satellite_name: str
    tle: TLEData
    metadata: SatelliteMetadata | None = None


class SatelliteCatalogStatus(BaseModel):
    satellite_count: int
    latest_tle_fetched_at: datetime | None
    source: str | None


"""
RADAR MODELS
"""


class RadarTrackPoint(BaseModel):
    timestamp: datetime
    azimuth_deg: float
    elevation_deg: float
    distance_km: float


class SatelliteInfo(BaseModel):
    satellite_id: str
    satellite_name: str
    owner: SatelliteOwner | None = None
    object_type: SatelliteObjectType | None = None
    launch: SatelliteLaunch | None = None


class SatelliteVisibility(BaseModel):
    visible_from: datetime
    visible_until: datetime
    max_elevation_deg: float


class SatellitePassPoint(BaseModel):
    azimuth_deg: float
    direction: str


class SatelliteRadarItem(BaseModel):
    info: SatelliteInfo
    visibility: SatelliteVisibility
    start: SatellitePassPoint
    end: SatellitePassPoint
    track: list[RadarTrackPoint]
