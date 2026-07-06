from datetime import UTC, datetime
from typing import Any

from skyfield.api import EarthSatellite, load

from app.models import (
    CelestrakSatelliteOutput,
    RadarSatelliteResult,
    RadarTrackPoint,
    SatelliteCatalogItem,
    SatelliteTLEUpdate,
    TLEData,
    TLEParsed,
)


def create_tle_data_lines(**kwargs: Any) -> list[str]:
    values = {
        "name": "ATLAS CENTAUR 2",
        "line1": "1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        "line2": "2 00694  30.3551  20.9180 0560095 134.0904 230.7205 14.08963668 62697",
    }
    values.update(kwargs)
    return [values["name"], values["line1"], values["line2"]]


def create_earth_satellite(**kwargs: Any) -> EarthSatellite:
    tle_data = create_tle_data_lines(**kwargs)
    ts = load.timescale()
    satellite = EarthSatellite(tle_data[1], tle_data[2], tle_data[0], ts)

    # # attach raw lines for tests if Skyfield instance does not expose them
    # satellite.line1 = tle_data[1]
    # satellite.line2 = tle_data[2]
    return satellite


def create_tle_parsed(**kwargs: Any) -> TLEParsed:
    data = {
        "epoch": datetime(2026, 2, 25, 12, 0, tzinfo=UTC),
        "inclination_deg": 30.3551,
        "raan_deg": 20.9180,
        "eccentricity": 0.0560095,
        "mean_motion_rev_per_day": 14.08963668,
        "drag_term_bstar": 0.000095096,
    }
    data.update(kwargs)
    return TLEParsed(**data)


def create_tle(**kwargs: Any) -> TLEData:
    parsed = kwargs.pop("parsed", None)
    data = {
        "line1": "1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        "line2": "2 00694  30.3551  20.9180 0560095 134.0904 230.7205 14.08963668 62697",
        "group": "visual",
        "source": "celestrak",
        "fetched_at": datetime(2026, 2, 25, 12, 0, tzinfo=UTC),
        "parsed": parsed if parsed is not None else create_tle_parsed(),
    }
    data.update(kwargs)
    return TLEData(**data)


def create_celestrak_output(**kwargs: Any) -> CelestrakSatelliteOutput:
    """
    Factory for creating a mock CelestrakSatelliteOutput object.
    """
    data = {
        "satellite_id": "12345",
        "satellite_name": "MockSatellite",
        "tle": create_tle(),
    }
    data.update(kwargs)
    return CelestrakSatelliteOutput(**data)


def create_satellite_tle_update(**kwargs: Any) -> SatelliteTLEUpdate:
    tle = kwargs.pop("tle", None)
    data = {
        "satellite_id": "12345",
        "satellite_name": "MockSatellite",
        "tle": tle if tle is not None else create_tle(),
    }
    data.update(kwargs)
    return SatelliteTLEUpdate(**data)


def create_satellite_catalog_item(**kwargs: Any) -> SatelliteCatalogItem:
    tle = kwargs.pop("tle", None)
    data = {
        "satellite_id": "12345",
        "satellite_name": "MockSatellite",
        "tle": tle if tle is not None else create_tle(),
    }
    data.update(kwargs)
    return SatelliteCatalogItem(**data)


def create_radar_track_point(**kwargs: Any) -> RadarTrackPoint:
    data = {
        "timestamp": datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
        "azimuth_deg": 45.0,
        "elevation_deg": 20.0,
        "distance_km": 1000.0,
    }
    data.update(kwargs)
    return RadarTrackPoint(**data)


def create_radar_result(**kwargs: Any) -> RadarSatelliteResult:
    track = kwargs.pop("track", None)
    visible_from = kwargs.pop("visible_from", None)
    visible_until = kwargs.pop("visible_until", None)

    default_track = (
        track
        if track is not None
        else [
            create_radar_track_point(),
        ]
    )

    data = {
        "satellite_id": "12345",
        "satellite_name": "MockSatellite",
        "visible_from": visible_from or default_track[0].timestamp,
        "visible_until": visible_until or default_track[-1].timestamp,
        "max_elevation_deg": 20.0,
        "start_azimuth_deg": 45.0,
        "start_direction": "NE",
        "end_azimuth_deg": 90.0,
        "end_direction": "E",
        "track": default_track,
    }
    data.update(kwargs)
    return RadarSatelliteResult(**data)
