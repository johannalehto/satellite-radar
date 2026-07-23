from datetime import UTC, datetime, timedelta

import pytest

from app.satellite_radar.builders import (
    azimuth_to_direction,
    build_satellite_radar_item,
    get_max_elevation,
)
from tests.factory import (
    create_radar_track_point,
    create_satellite_catalog_item,
    create_satellite_metadata,
)


def test_get_max_elevation_returns_highest_elevation() -> None:
    track = [
        create_radar_track_point(elevation_deg=12.0),
        create_radar_track_point(elevation_deg=35.0),
        create_radar_track_point(elevation_deg=20.0),
    ]

    assert get_max_elevation(track) == 35.0


def test_build_satellite_radar_item_builds_nested_response() -> None:
    visible_from = datetime(2026, 3, 25, 12, 0, tzinfo=UTC)
    visible_until = visible_from + timedelta(minutes=1)

    catalog_item = create_satellite_catalog_item(
        satellite_id="00694",
        satellite_name="ATLAS CENTAUR 2",
    )
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

    result = build_satellite_radar_item(catalog_item, track)

    assert result.info.satellite_id == "00694"
    assert result.info.satellite_name == "ATLAS CENTAUR 2"
    assert result.visibility.visible_from == visible_from
    assert result.visibility.visible_until == visible_until
    assert result.visibility.max_elevation_deg == 30.0
    assert result.start.azimuth_deg == 45.0
    assert result.start.direction == "NE"
    assert result.end.azimuth_deg == 90.0
    assert result.end.direction == "E"
    assert result.track == track


def test_build_satellite_radar_item_maps_catalog_metadata_to_info() -> None:
    launch_date = datetime(1963, 11, 27, tzinfo=UTC).date()
    catalog_item = create_satellite_catalog_item(
        metadata=create_satellite_metadata(
            owner="US",
            object_type="ROCKET BODY",
            launch_date=launch_date,
            launch_site="AFETR",
        ),
    )
    track = [create_radar_track_point()]

    result = build_satellite_radar_item(catalog_item, track)

    assert result.info.owner == "US"
    assert result.info.object_type == "ROCKET BODY"
    assert result.info.launch_date == launch_date
    assert result.info.launch_site == "AFETR"


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
    assert azimuth_to_direction(azimuth_deg) == expected
