import pytest

from app.satellite_radar.builders import azimuth_to_direction, get_max_elevation
from tests.factory import create_radar_track_point


def test_get_max_elevation_returns_highest_elevation() -> None:
    track = [
        create_radar_track_point(elevation_deg=12.0),
        create_radar_track_point(elevation_deg=35.0),
        create_radar_track_point(elevation_deg=20.0),
    ]

    assert get_max_elevation(track) == 35.0


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
