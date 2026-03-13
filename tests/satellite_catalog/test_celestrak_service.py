import pytest
from skyfield.api import load

from app.models import CelestrakSatelliteOutput, Position
from app.satellite_catalog.celestrak_service import CelestrakService
from tests.factory import create_earth_satellite


@pytest.fixture
def timescale():
    ts = load.timescale()
    return ts


@pytest.fixture
def satellites():
    return [create_earth_satellite()]


def test_generate_time_intervals(timescale):
    service = CelestrakService()
    start_time = timescale.now().utc_datetime()
    intervals = service.generate_time_intervals(start_time)

    assert len(intervals) == (26 * 60) // 60  # 26 hours, every 60 minutes
    assert intervals[0].utc_datetime().minute == start_time.minute


def test_calculate_positions(timescale, satellites):
    service = CelestrakService()

    service.satellites = satellites
    results = service.calculate_positions()

    assert len(results) == 1
    assert results[0].satellite_name == "ATLAS CENTAUR 2"
    assert results[0].satellite_id == "00694"
    assert isinstance(results[0], CelestrakSatelliteOutput)

    # Check positions
    assert len(results[0].next_positions) > 0
    position = results[0].next_positions[0]
    assert isinstance(position, Position)
    # assert position.latitude == 60.0
    # assert position.longitude == 24.0
    # assert position.altitude_km == 500.0


def test_fetch_tles_returns_outputs_with_tle_data() -> None:
    service = CelestrakService()
    service.satellites = [create_earth_satellite()]

    results = service.fetch_tles()

    assert len(results) == 1
    assert isinstance(results[0], CelestrakSatelliteOutput)
    assert results[0].satellite_name == "ATLAS CENTAUR 2"
    assert results[0].satellite_id == "00694"

    assert results[0].tle is not None
    assert results[0].tle.line1.startswith("1 00694U")
    assert results[0].tle.line2.startswith("2 00694")
    assert results[0].tle.group == "visual"
    assert results[0].tle.source == "celestrak"

    assert results[0].tle.parsed.inclination_deg is not None
    assert results[0].tle.parsed.raan_deg is not None
    assert results[0].tle.parsed.eccentricity is not None
    assert results[0].tle.parsed.mean_motion_rev_per_day is not None
    assert results[0].tle.parsed.drag_term_bstar is not None
