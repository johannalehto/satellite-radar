from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from app.satellite_radar.service import SatelliteRadarService
from tests.factory import (
    create_earth_satellite,
    create_radar_track_point,
    create_satellite_catalog_item,
)


def test_get_visible_track_filters_points_below_minimum_elevation() -> None:
    track = [
        create_radar_track_point(elevation_deg=5.0),
        create_radar_track_point(elevation_deg=10.0),
        create_radar_track_point(elevation_deg=30.0),
    ]

    result = SatelliteRadarService.get_visible_track(track)

    assert [p.elevation_deg for p in result] == [10.0, 30.0]


def test_get_max_elevation_returns_highest_elevation() -> None:
    track = [
        create_radar_track_point(elevation_deg=12.0),
        create_radar_track_point(elevation_deg=35.0),
        create_radar_track_point(elevation_deg=20.0),
    ]

    assert SatelliteRadarService.get_max_elevation(track) == 35.0


@pytest.mark.parametrize(
    ("azimuth_deg", "expected"),
    [
        (0.0, "N"),
        (45.0, "NE"),
        (90.0, "E"),
        (135.0, "SE"),
        (180.0, "S"),
        (225.0, "SW"),
        (270.0, "W"),
        (315.0, "NW"),
        (360.0, "N"),
    ],
)
def test_azimuth_to_direction(azimuth_deg: float, expected: str) -> None:
    assert SatelliteRadarService.azimuth_to_direction(azimuth_deg) == expected


def test_calculate_satellite_track_raises_for_naive_start_time() -> None:
    satellite_catalog = Mock()
    service = SatelliteRadarService(satellite_catalog=satellite_catalog)

    with pytest.raises(ValueError, match="start_time must be timezone-aware"):
        service.calculate_satellite_track(
            Mock(),
            observer_lat=60.1699,
            observer_lon=24.9384,
            start_time=datetime(2026, 3, 25, 12, 0),  # naive
            total_minutes=10,
            step_seconds=60,
        )


def test_get_visible_satellites_returns_empty_when_calculation_returns_no_points() -> None:
    satellite_catalog = Mock()
    satellite_catalog.get_all_satellites.return_value = [create_satellite_catalog_item()]

    service = SatelliteRadarService(satellite_catalog=satellite_catalog)

    # Patch calculation to return an empty list (no passes)
    with patch.object(service, "calculate_satellite_track", return_value=[]):
        results = service.get_visible_satellites(
            lat=60.1699,
            lon=24.9384,
            now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
        )

    assert results == []


def test_get_visible_satellites_skips_tracks_below_minimum_elevation() -> None:
    satellite_catalog = Mock()
    satellite_catalog.get_all_satellites.return_value = [create_satellite_catalog_item()]

    service = SatelliteRadarService(satellite_catalog=satellite_catalog)

    low_track = [
        create_radar_track_point(elevation_deg=2.0),
        create_radar_track_point(elevation_deg=5.0),
        create_radar_track_point(elevation_deg=3.0),
    ]

    # Only patch calculation; service should filter these out
    with patch.object(service, "calculate_satellite_track", return_value=low_track):
        results = service.get_visible_satellites(
            lat=60.1699,
            lon=24.9384,
            now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
        )

    assert results == []


def test_get_visible_satellites_builds_result_from_visible_track() -> None:
    now = datetime(2026, 3, 25, 12, 0, tzinfo=UTC)
    visible_from = now
    visible_until = now + timedelta(minutes=1)

    satellite_catalog = Mock()
    satellite_catalog.get_all_satellites.return_value = [
        create_satellite_catalog_item(
            satellite_id="694",
            satellite_name="ATLAS CENTAUR 2",
        )
    ]

    service = SatelliteRadarService(satellite_catalog=satellite_catalog)

    track = [
        create_radar_track_point(
            timestamp=visible_from,
            azimuth_deg=45.0,
            elevation_deg=20.0,
        ),
        create_radar_track_point(
            timestamp=visible_until,
            azimuth_deg=90.0,
            elevation_deg=30.0,
        ),
    ]

    # Patch both building and calculation - we only want to test result assembly
    with (
        patch.object(service, "build_earth_satellite", return_value=Mock()),
        patch.object(service, "calculate_satellite_track", return_value=track),
    ):
        results = service.get_visible_satellites(lat=60.1699, lon=24.9384, now=now)

    assert len(results) == 1
    r = results[0]
    assert r.info.satellite_id == "694"
    assert r.info.satellite_name == "ATLAS CENTAUR 2"
    assert r.visibility.visible_from == visible_from
    assert r.visibility.visible_until == visible_until
    assert r.visibility.max_elevation_deg == 30.0
    assert r.start.direction == "NE"
    assert r.end.direction == "E"
    assert r.track == track


def test_get_visible_satellites_applies_limit() -> None:
    satellite_catalog = Mock()
    satellite_catalog.get_all_satellites.return_value = [
        create_satellite_catalog_item(satellite_id="1"),
        create_satellite_catalog_item(satellite_id="2"),
    ]

    service = SatelliteRadarService(satellite_catalog=satellite_catalog)

    # Patch so both items produce one visible point
    with (
        patch.object(service, "build_earth_satellite", return_value=Mock()),
        patch.object(
            service,
            "calculate_satellite_track",
            return_value=[create_radar_track_point(elevation_deg=20.0)],
        ),
    ):
        results = service.get_visible_satellites(
            lat=60.1699,
            lon=24.9384,
            limit=1,
            now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
        )

    assert len(results) == 1


def test_calculate_satellite_track_returns_expected_number_of_points_and_timestamps() -> None:
    sat = create_earth_satellite()
    start = datetime(2026, 3, 25, 12, 0, tzinfo=UTC)
    total_minutes = 1
    step_seconds = 30

    points = SatelliteRadarService.calculate_satellite_track(
        sat,
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


def test_calculate_satellite_track_point_fields_are_floats_and_preserve_timezone() -> None:
    sat = create_earth_satellite()
    # use a non-UTC timezone to ensure timezone(UTC) conversion inside method doesnt
    # mutate returned timestamps

    tz = timezone(timedelta(hours=2))
    start = datetime(2026, 3, 25, 14, 0, tzinfo=tz)  # same instant as 12:00 UTC

    points = SatelliteRadarService.calculate_satellite_track(
        sat,
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
        # timestamp should preserve the original tzinfo used for start_time computations
        assert p.timestamp.tzinfo == tz
