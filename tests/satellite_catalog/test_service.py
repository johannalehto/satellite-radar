from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models import SatelliteCatalogStatus, SatelliteTLEUpdate
from app.satellite_catalog.service import SatelliteCatalogService
from tests.factory import create_celestrak_output, create_tle


@pytest.fixture
def celestrak_outputs():
    return [
        create_celestrak_output(satellite_id="12345", satellite_name="MockSat-1"),
        create_celestrak_output(satellite_id="67890", satellite_name="MockSat-2"),
    ]


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


def test_get_catalog_status_returns_repository_status() -> None:
    catalog_status = SatelliteCatalogStatus(
        satellite_count=157,
        latest_tle_fetched_at=datetime(2026, 7, 21, 12, 0, tzinfo=UTC),
        source="celestrak",
    )
    mock_repo = MagicMock()
    mock_repo.get_catalog_status.return_value = catalog_status

    service = SatelliteCatalogService(repository=mock_repo)

    assert service.get_catalog_status() == catalog_status
    mock_repo.get_catalog_status.assert_called_once_with()
