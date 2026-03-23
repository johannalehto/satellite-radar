from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models import SatelliteTLEUpdate
from app.satellite_catalog.service import SatelliteCatalogService
from tests.factory import create_celestrak_output, create_tle


@pytest.fixture
def celestrak_outputs():
    return [
        create_celestrak_output(satellite_id="12345", satellite_name="MockSat-1"),
        create_celestrak_output(satellite_id="67890", satellite_name="MockSat-2"),
    ]


def test_get_satellites_from_catalog_returns_empty_when_no_results() -> None:
    mock_repository = MagicMock()
    mock_repository.get_satellite_data_from_db.return_value = []

    service = SatelliteCatalogService(celestrak_service=MagicMock(), repository=mock_repository)

    result = service.get_satellites_from_catalog(
        lat=60.0,
        lon=24.0,
        now=datetime(2026, 2, 25, tzinfo=UTC),
    )

    assert result.location == (60.0, 24.0)
    assert result.satellites == []


def test_to_tle_updates_maps_outputs_with_tle() -> None:
    outputs = [
        create_celestrak_output(
            satellite_id="12345",
            satellite_name="MockSat-1",
            tle=create_tle(),
            next_positions=None,
        ),
        create_celestrak_output(
            satellite_id="67890",
            satellite_name="MockSat-2",
            tle=create_tle(),
            next_positions=None,
        ),
    ]

    updates = SatelliteCatalogService._to_tle_updates(outputs)

    assert len(updates) == 2
    assert all(isinstance(update, SatelliteTLEUpdate) for update in updates)
    assert updates[0].satellite_id == "12345"
    assert updates[0].satellite_name == "MockSat-1"
    assert updates[0].tle is not None
    assert updates[1].satellite_id == "67890"
    assert updates[1].satellite_name == "MockSat-2"
    assert updates[1].tle is not None


def test_to_tle_updates_skips_outputs_without_tle() -> None:
    outputs = [
        create_celestrak_output(
            satellite_id="12345",
            satellite_name="MockSat-1",
            tle=create_tle(),
        ),
        create_celestrak_output(
            satellite_id="67890",
            satellite_name="MockSat-2",
            tle=None,
        ),
    ]

    updates = SatelliteCatalogService._to_tle_updates(outputs)

    assert len(updates) == 1
    assert updates[0].satellite_id == "12345"


def test_update_satellite_catalog_with_tle_data_calls_repo_with_mapped_updates() -> None:
    outputs = [
        create_celestrak_output(
            satellite_id="12345",
            satellite_name="MockSat-1",
            tle=create_tle(),
        ),
        create_celestrak_output(
            satellite_id="67890",
            satellite_name="MockSat-2",
            tle=create_tle(),
        ),
    ]

    mock_celestrak = MagicMock()
    mock_repo = MagicMock()
    mock_celestrak.fetch_tles.return_value = outputs

    service = SatelliteCatalogService(
        celestrak_service=mock_celestrak,
        repository=mock_repo,
    )

    service.update_satellite_catalog_with_tle_data()

    mock_celestrak.fetch_tles.assert_called_once_with()
    mock_repo.upsert_tles_to_db.assert_called_once()

    tle_updates = mock_repo.upsert_tles_to_db.call_args.args[0]
    assert len(tle_updates) == 2
    assert tle_updates[0].satellite_id == "12345"
    assert tle_updates[0].satellite_name == "MockSat-1"
    assert tle_updates[0].tle is not None
