from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest
from skyfield.api import EarthSatellite, load

from app.models import (
    CelestrakSatelliteOutput,
    Position,
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

    # attach raw lines for tests if Skyfield instance does not expose them
    satellite.line1 = tle_data[1]
    satellite.line2 = tle_data[2]
    return satellite


def create_position(**kwargs: Any) -> Position:
    data = {
        "timestamp": datetime.fromisoformat("2024-11-03T12:00:00+00:00"),
        "latitude": 60.0,
        "longitude": 24.0,
        "altitude_km": 500.0,
    }
    data.update(kwargs)
    return Position(**data)


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
        "next_positions": [create_position()],
        "fetched_at": datetime.now(UTC),
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


@pytest.fixture
def create_timescale():
    ts = load.timescale()
    return ts


# TODO: These are old and should be deprecated
@pytest.fixture
def create_satellite():
    satellite = MagicMock()
    satellite.name = "MockSatellite"
    satellite.satnum = 12345
    satellite.at.return_value.subpoint.return_value = MagicMock(
        latitude=MagicMock(degrees=60.0),
        longitude=MagicMock(degrees=24.0),
        elevation=MagicMock(km=500.0),
    )
    return satellite


@pytest.fixture
def create_satellites(create_satellite):
    return [create_satellite]
