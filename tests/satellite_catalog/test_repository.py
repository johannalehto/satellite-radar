from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models import SatellitePosition
from app.satellite_catalog.repository import SatelliteCatalogRepository
from app.satellite_catalog.service import SatelliteCatalogService
from tests.factory import create_celestrak_output, create_position, create_satellite_tle_update


@pytest.fixture
def celestrak_outputs():
    return [
        create_celestrak_output(satellite_id="12345", satellite_name="MockSat-1"),
        create_celestrak_output(satellite_id="67890", satellite_name="MockSat-2"),
    ]


def test_update_satellite_catalog_calls_repo_with_mapped_positions(celestrak_outputs):
    mock_celestrak = MagicMock()
    mock_repo = MagicMock()

    mock_celestrak.calculate_positions.return_value = celestrak_outputs

    service = SatelliteCatalogService(
        celestrak_service=mock_celestrak,
        repository=mock_repo,
    )

    service.update_satellite_catalog()

    mock_repo.upsert_positions_to_db.assert_called_once()
    positions = mock_repo.upsert_positions_to_db.call_args.args[0]

    assert len(positions) == 2
    assert positions[0].satellite_id == "12345"


def test_upsert_positions_to_db_builds_updateone_with_upsert_true() -> None:
    mock_collection = MagicMock()
    mock_bulk_result = MagicMock(
        matched_count=0,
        modified_count=0,
        upserted_count=1,
    )
    mock_collection.bulk_write.return_value = mock_bulk_result

    repository = SatelliteCatalogRepository(collection=mock_collection)

    satellite_position = SatellitePosition(
        satellite_id="12345",
        satellite_name="MockSat-1",
        next_positions=[create_position()],
        fetched_at=datetime(2026, 2, 25, 0, 0, tzinfo=UTC),
    )

    repository.upsert_positions_to_db([satellite_position])

    mock_collection.bulk_write.assert_called_once()

    update_operations = mock_collection.bulk_write.call_args.args[0]
    assert len(update_operations) == 1

    update_operation = update_operations[0]

    assert update_operation._filter == {"satellite_id": "12345"}
    assert update_operation._doc == {"$set": satellite_position.model_dump()}
    assert update_operation._upsert is True


def test_get_satellite_data_from_db_calls_find_with_expected_query() -> None:
    mock_collection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = [{"satellite_id": "12345"}]
    mock_collection.find.return_value = mock_cursor

    repository = SatelliteCatalogRepository(collection=mock_collection)

    latitude = 60.0
    longitude = 24.0
    timestamp = datetime(2026, 2, 25, 0, 0, tzinfo=UTC)

    result = repository.get_satellite_data_from_db(latitude, longitude, timestamp)

    mock_collection.find.assert_called_once_with(
        {},
        projection={"_id": 0, "satellite_id": 1, "satellite_name": 1, "fetched_at": 1},
    )
    mock_cursor.limit.assert_called_once_with(10)
    assert result == [{"satellite_id": "12345"}]


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
