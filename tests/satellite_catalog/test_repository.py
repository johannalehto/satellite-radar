from unittest.mock import MagicMock

import pytest

from app.satellite_catalog.repository import SatelliteCatalogRepository
from tests.factory import create_celestrak_output, create_satellite_tle_update


@pytest.fixture
def celestrak_outputs():
    return [
        create_celestrak_output(satellite_id="12345", satellite_name="MockSat-1"),
        create_celestrak_output(satellite_id="67890", satellite_name="MockSat-2"),
    ]


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
