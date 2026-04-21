from datetime import UTC, datetime
from unittest.mock import Mock

from app.satellite_radar.service import SatelliteRadarService
from tests.factory import create_satellite_catalog_item


def test_get_visible_satellites_returns_results() -> None:
    satellite_catalog = Mock()
    satellite_catalog.get_all_satellites.return_value = [create_satellite_catalog_item()]

    service = SatelliteRadarService(satellite_catalog=satellite_catalog)

    results = service.get_visible_satellites(
        lat=60.1699,
        lon=24.9384,
        minutes_ahead=5,
        step_seconds=60,
        now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
    )

    assert isinstance(results, list)
    satellite_catalog.get_all_satellites.assert_called_once()


def test_get_visible_satellites_returns_radar_results() -> None:
    satellite_catalog = Mock()
    satellite_catalog.get_all_satellites.return_value = [
        create_satellite_catalog_item(
            satellite_id="694",
            satellite_name="ATLAS CENTAUR 2",
        )
    ]

    service = SatelliteRadarService(satellite_catalog=satellite_catalog)

    results = service.get_visible_satellites(
        lat=60.1699,
        lon=24.9384,
        minutes_ahead=5,
        step_seconds=60,
        now=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
    )

    assert isinstance(results, list)

    if results:
        result = results[0]
        assert result.satellite_id == "694"
        assert result.satellite_name == "ATLAS CENTAUR 2"
        assert len(result.track) > 0
