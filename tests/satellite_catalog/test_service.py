from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.models import SatelliteCatalogStatus, SatelliteTLEUpdate
from app.satellite_catalog.service import SatelliteCatalogService
from tests.factory import create_satellite_metadata_update, create_satellite_tle_update


def test_update_satellite_catalog_with_tle_data_upserts_fetched_tle_updates() -> None:
    tle_updates = [
        create_satellite_tle_update(
            satellite_id="12345",
            satellite_name="MockSat-1",
        ),
        create_satellite_tle_update(
            satellite_id="67890",
            satellite_name="MockSat-2",
        ),
    ]

    mock_celestrak = MagicMock()
    mock_repo = MagicMock()
    mock_celestrak.fetch_tles.return_value = tle_updates

    service = SatelliteCatalogService(
        celestrak_service=mock_celestrak,
        repository=mock_repo,
    )

    service.update_satellite_catalog_with_tle_data()

    mock_celestrak.fetch_tles.assert_called_once_with()
    mock_repo.upsert_tles_to_db.assert_called_once()

    passed_tle_updates = mock_repo.upsert_tles_to_db.call_args.args[0]
    assert passed_tle_updates == tle_updates
    assert all(isinstance(update, SatelliteTLEUpdate) for update in passed_tle_updates)


def test_update_satellite_catalog_with_metadata_updates_repository_metadata() -> None:
    metadata_updates = [
        create_satellite_metadata_update(
            satellite_id="12345",
            satellite_name="MockSat-1",
        ),
        create_satellite_metadata_update(
            satellite_id="67890",
            satellite_name="MockSat-2",
        ),
    ]

    mock_celestrak = MagicMock()
    mock_repo = MagicMock()
    mock_celestrak.fetch_satcat_metadata.return_value = metadata_updates

    service = SatelliteCatalogService(
        celestrak_service=mock_celestrak,
        repository=mock_repo,
    )

    service.update_satellite_catalog_with_metadata()

    mock_celestrak.fetch_satcat_metadata.assert_called_once_with()
    mock_repo.update_metadata_in_db.assert_called_once_with(metadata_updates)
    mock_repo.upsert_tles_to_db.assert_not_called()


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
