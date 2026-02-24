from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest
from skyfield.api import EarthSatellite, load

from app.models import CelestrakSatelliteOutput, Position


def create_tle_data(**kwargs: Any) -> list[str]:
    values = {
        "name": "ATLAS CENTAUR 2",
        "line1": "1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        "line2": "2 00694  30.3551  20.9180 0560095 134.0904 230.7205 14.08963668 62697",
    }
    values.update(kwargs)
    return [values["name"], values["line1"], values["line2"]]


def create_earth_satellite(**kwargs: Any) -> EarthSatellite:
    tle_data = create_tle_data(**kwargs)
    ts = load.timescale()
    return EarthSatellite(tle_data[1], tle_data[2], tle_data[0], ts)


def create_position(**kwargs: Any) -> Position:
    data = {
        "timestamp": datetime.fromisoformat("2024-11-03T12:00:00+00:00"),
        "latitude": 60.0,
        "longitude": 24.0,
        "altitude_km": 500.0,
    }
    data.update(kwargs)
    return Position(**data)


def create_celestrak_output(**kwargs: Any) -> CelestrakSatelliteOutput:
    """
    Factory for creating a mock CelestrakSatelliteOutput object.
    """
    next_positions = kwargs.pop("next_positions", None)
    data = {
        "satellite_id": "12345",
        "satellite_name": "MockSatellite",
        "next_positions": next_positions if next_positions is not None else [create_position()],
        "fetched_at": datetime.now(UTC),
    }
    data.update(kwargs)
    return CelestrakSatelliteOutput(**data)


@pytest.fixture
def create_timescale():
    ts = load.timescale()
    return ts


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
