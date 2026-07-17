from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.satellite_radar.track_calculator import SkyfieldSatelliteTrackCalculator
from tests.factory import create_satellite_catalog_item


def test_calculate_track_raises_for_naive_start_time() -> None:
    calculator = SkyfieldSatelliteTrackCalculator()

    with pytest.raises(ValueError, match="start_time must be timezone-aware"):
        calculator.calculate_track(
            create_satellite_catalog_item(),
            observer_lat=60.1699,
            observer_lon=24.9384,
            start_time=datetime(2026, 3, 25, 12, 0),
            total_minutes=10,
            step_seconds=60,
        )


def test_calculate_track_returns_expected_number_of_points_and_timestamps() -> None:
    calculator = SkyfieldSatelliteTrackCalculator()
    start = datetime(2026, 3, 25, 12, 0, tzinfo=UTC)
    total_minutes = 1
    step_seconds = 30

    points = calculator.calculate_track(
        create_satellite_catalog_item(),
        observer_lat=60.1699,
        observer_lon=24.9384,
        start_time=start,
        total_minutes=total_minutes,
        step_seconds=step_seconds,
    )

    expected_steps = (total_minutes * 60) // step_seconds + 1
    assert len(points) == expected_steps

    expected_times = [start + timedelta(seconds=i * step_seconds) for i in range(expected_steps)]
    assert [p.timestamp for p in points] == expected_times


def test_calculate_track_point_fields_are_floats_and_preserve_timezone() -> None:
    calculator = SkyfieldSatelliteTrackCalculator()
    tz = timezone(timedelta(hours=2))
    start = datetime(2026, 3, 25, 14, 0, tzinfo=tz)

    points = calculator.calculate_track(
        create_satellite_catalog_item(),
        observer_lat=60.1699,
        observer_lon=24.9384,
        start_time=start,
        total_minutes=1,
        step_seconds=30,
    )

    assert points, "expected at least one point"
    for p in points:
        assert isinstance(p.azimuth_deg, float)
        assert isinstance(p.elevation_deg, float)
        assert isinstance(p.distance_km, float)
        assert p.timestamp.tzinfo == tz
