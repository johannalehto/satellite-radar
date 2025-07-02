import pytest
from unittest.mock import MagicMock
from skyfield.api import Topos, load
from app.models import Position, CelestrakSatelliteOutput


from typing import Any
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


def create_celestrak_output(**kwargs: Any) -> CelestrakSatelliteOutput:
    """
    Factory for creating a mock CelestrakSatelliteOutput object.
    """
    positions = kwargs.pop(
        "next_positions",
        [
            Position(
                timestamp="2024-11-03T12:00:00Z",
                latitude=60.0,
                longitude=24.0,
                altitude_km=500.0,
            )
        ],
    )

    return CelestrakSatelliteOutput(
        id=kwargs.get("id", 12345),
        satellite_name=kwargs.get("satellite_name", "MockSatellite"),
        next_positions=positions,
        fetched_at=datetime.now(),
    )


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
