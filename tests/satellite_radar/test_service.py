from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from app.models import RadarTrackPoint, SatelliteCatalogItem
from app.satellite_radar.errors import SatelliteRadarCatalogUnavailableError
from app.satellite_radar.service import SatelliteRadarService
from tests.factory import (
    create_radar_track_point,
    create_satellite_catalog_item,
)


class StubSatelliteCatalog:
    def __init__(self, satellites: list[SatelliteCatalogItem]):
        self.satellites = satellites

    def get_all_satellites(self) -> list[SatelliteCatalogItem]:
        return self.satellites


class FailingSatelliteCatalog:
    def get_all_satellites(self) -> list[SatelliteCatalogItem]:
        raise RuntimeError("database unavailable")


class StubSatelliteTrackCalculator:
    def __init__(self, tracks_by_satellite_id: dict[str, list[RadarTrackPoint]]):
        self.tracks_by_satellite_id = tracks_by_satellite_id

    def calculate_track(
        self,
        catalog_item: SatelliteCatalogItem,
        **_: Any,
    ) -> list[RadarTrackPoint]:
        return self.tracks_by_satellite_id[catalog_item.satellite_id]


class FailingSatelliteTrackCalculator:
    def calculate_track(
        self,
        catalog_item: SatelliteCatalogItem,
        **_: Any,
    ) -> list[RadarTrackPoint]:
        raise RuntimeError(f"bad TLE for {catalog_item.satellite_id}")


def test_get_visible_track_filters_points_below_minimum_elevation() -> None:
    track = [
        create_radar_track_point(elevation_deg=5.0),
        create_radar_track_point(elevation_deg=10.0),
        create_radar_track_point(elevation_deg=30.0),
    ]

    result = SatelliteRadarService.get_visible_track(track)

    assert [p.elevation_deg for p in result] == [10.0, 30.0]


def test_get_visible_satellites_returns_empty_when_calculation_returns_no_points() -> None:
    catalog_item = create_satellite_catalog_item()
    service = SatelliteRadarService(
        satellite_catalog=StubSatelliteCatalog([catalog_item]),
        track_calculator=StubSatelliteTrackCalculator(
            tracks_by_satellite_id={catalog_item.satellite_id: []}
        ),
    )

    results = service.get_visible_satellites(
        lat=60.1699,
        lon=24.9384,
        now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
    )

    assert results == []


def test_get_visible_satellites_skips_tracks_below_minimum_elevation() -> None:
    catalog_item = create_satellite_catalog_item()

    low_track = [
        create_radar_track_point(elevation_deg=2.0),
        create_radar_track_point(elevation_deg=5.0),
        create_radar_track_point(elevation_deg=3.0),
    ]

    service = SatelliteRadarService(
        satellite_catalog=StubSatelliteCatalog([catalog_item]),
        track_calculator=StubSatelliteTrackCalculator(
            tracks_by_satellite_id={catalog_item.satellite_id: low_track}
        ),
    )

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

    service = SatelliteRadarService(
        satellite_catalog=StubSatelliteCatalog([catalog_item]),
        track_calculator=StubSatelliteTrackCalculator(
            tracks_by_satellite_id={catalog_item.satellite_id: track}
        ),
    )

    results = service.get_visible_satellites(lat=60.1699, lon=24.9384, now=now)

    assert len(results) == 1
    r = results[0]
    assert r.info.satellite_id == "00694"
    assert r.info.satellite_name == "ATLAS CENTAUR 2"
    assert r.visibility.visible_from == visible_from
    assert r.visibility.visible_until == visible_until
    assert r.visibility.max_elevation_deg == 30.0
    assert r.start.direction == "NE"
    assert r.end.direction == "E"
    assert r.track == track


def test_get_visible_satellites_applies_limit() -> None:
    catalog_items = [
        create_satellite_catalog_item(satellite_id="00694"),
        create_satellite_catalog_item(satellite_id="25544"),
    ]

    service = SatelliteRadarService(
        satellite_catalog=StubSatelliteCatalog(catalog_items),
        track_calculator=StubSatelliteTrackCalculator(
            tracks_by_satellite_id={
                item.satellite_id: [create_radar_track_point(elevation_deg=20.0)]
                for item in catalog_items
            }
        ),
    )

    results = service.get_visible_satellites(
        lat=60.1699,
        lon=24.9384,
        limit=1,
        now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
    )

    assert len(results) == 1


def test_get_visible_satellites_sorts_by_visible_until() -> None:
    now = datetime(2026, 3, 25, 12, 0, tzinfo=UTC)
    later_visible_satellite = create_satellite_catalog_item(
        satellite_id="00694",
        satellite_name="ATLAS CENTAUR 2",
    )
    earlier_visible_satellite = create_satellite_catalog_item(
        satellite_id="25544",
        satellite_name="ISS (ZARYA)",
    )

    service = SatelliteRadarService(
        satellite_catalog=StubSatelliteCatalog(
            [
                later_visible_satellite,
                earlier_visible_satellite,
            ]
        ),
        track_calculator=StubSatelliteTrackCalculator(
            tracks_by_satellite_id={
                later_visible_satellite.satellite_id: [
                    create_radar_track_point(
                        timestamp=now + timedelta(minutes=5),
                        elevation_deg=20.0,
                    )
                ],
                earlier_visible_satellite.satellite_id: [
                    create_radar_track_point(
                        timestamp=now + timedelta(minutes=1),
                        elevation_deg=20.0,
                    )
                ],
            }
        ),
    )

    results = service.get_visible_satellites(
        lat=60.1699,
        lon=24.9384,
        limit=10,
        now=now,
    )

    assert [result.info.satellite_id for result in results] == ["25544", "00694"]


def test_get_visible_satellites_raises_when_catalog_is_unavailable() -> None:
    service = SatelliteRadarService(
        satellite_catalog=FailingSatelliteCatalog(),
        track_calculator=StubSatelliteTrackCalculator(tracks_by_satellite_id={}),
    )

    with pytest.raises(SatelliteRadarCatalogUnavailableError):
        service.get_visible_satellites(
            lat=60.1699,
            lon=24.9384,
            now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
        )


def test_get_visible_satellites_skips_satellite_when_track_calculation_fails() -> None:
    service = SatelliteRadarService(
        satellite_catalog=StubSatelliteCatalog(
            [create_satellite_catalog_item(satellite_id="00694")]
        ),
        track_calculator=FailingSatelliteTrackCalculator(),
    )

    results = service.get_visible_satellites(
        lat=60.1699,
        lon=24.9384,
        now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
    )

    assert results == []
