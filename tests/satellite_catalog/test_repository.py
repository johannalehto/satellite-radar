from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.satellite_catalog.repository import SatelliteCatalogRepository
from tests.factory import create_satellite_metadata_update, create_satellite_tle_update


def test_upsert_tles_to_db_builds_updateone_with_expected_fields() -> None:
    mock_collection = MagicMock()
    mock_bulk_result = MagicMock(
        matched_count=0,
        modified_count=0,
        upserted_count=1,
    )
    mock_collection.bulk_write.return_value = mock_bulk_result

    repository = SatelliteCatalogRepository(collection=mock_collection)

    tle_update = create_satellite_tle_update(
        satellite_id="12345",
        satellite_name="MockSat-1",
    )

    repository.upsert_tles_to_db([tle_update])

    mock_collection.bulk_write.assert_called_once()

    update_operations = mock_collection.bulk_write.call_args.args[0]
    assert len(update_operations) == 1

    update_operation = update_operations[0]

    assert update_operation._filter == {"satellite_id": "12345"}
    assert update_operation._doc == {
        "$set": {
            "satellite_id": "12345",
            "satellite_name": "MockSat-1",
            "tle": tle_update.tle.model_dump(),
        }
    }
    assert update_operation._upsert is True


def test_upsert_tles_to_db_returns_early_for_empty_input() -> None:
    mock_collection = MagicMock()
    repository = SatelliteCatalogRepository(collection=mock_collection)

    repository.upsert_tles_to_db([])

    mock_collection.bulk_write.assert_not_called()


def test_update_metadata_in_db_builds_updateone_with_expected_fields() -> None:
    mock_collection = MagicMock()
    mock_bulk_result = MagicMock(
        matched_count=1,
        modified_count=1,
    )
    mock_collection.bulk_write.return_value = mock_bulk_result

    repository = SatelliteCatalogRepository(collection=mock_collection)

    metadata_update = create_satellite_metadata_update(
        satellite_id="12345",
        satellite_name="MockSat-1",
    )

    repository.update_metadata_in_db([metadata_update])

    mock_collection.bulk_write.assert_called_once()

    update_operations = mock_collection.bulk_write.call_args.args[0]
    assert len(update_operations) == 1

    update_operation = update_operations[0]

    assert update_operation._filter == {"satellite_id": "12345"}
    assert update_operation._doc == {
        "$set": {
            "satellite_name": "MockSat-1",
            "metadata": metadata_update.metadata.model_dump(mode="json"),
        }
    }
    assert update_operation._upsert is False


def test_update_metadata_in_db_returns_early_for_empty_input() -> None:
    mock_collection = MagicMock()
    repository = SatelliteCatalogRepository(collection=mock_collection)

    repository.update_metadata_in_db([])

    mock_collection.bulk_write.assert_not_called()


def test_get_catalog_status_returns_count_and_latest_tle_metadata() -> None:
    latest_fetched_at = datetime(2026, 7, 21, 12, 0, tzinfo=UTC)
    mock_collection = MagicMock()
    mock_collection.count_documents.return_value = 157
    mock_collection.find_one.return_value = {
        "tle": {
            "fetched_at": latest_fetched_at,
            "source": "celestrak",
        }
    }

    repository = SatelliteCatalogRepository(collection=mock_collection)

    status = repository.get_catalog_status()

    mock_collection.count_documents.assert_called_once_with({})
    mock_collection.find_one.assert_called_once()
    assert status.satellite_count == 157
    assert status.latest_tle_fetched_at == latest_fetched_at
    assert status.source == "celestrak"


def test_get_catalog_status_returns_empty_metadata_when_catalog_is_empty() -> None:
    mock_collection = MagicMock()
    mock_collection.count_documents.return_value = 0
    mock_collection.find_one.return_value = None

    repository = SatelliteCatalogRepository(collection=mock_collection)

    status = repository.get_catalog_status()

    assert status.satellite_count == 0
    assert status.latest_tle_fetched_at is None
    assert status.source is None
