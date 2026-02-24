from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.satellite_catalog.service import SatelliteCatalogService
from tests.factory import create_celestrak_output, create_position


@pytest.fixture
def celestrak_outputs():
    return [
        create_celestrak_output(satellite_id="12345", satellite_name="MockSat-1"),
        create_celestrak_output(satellite_id="67890", satellite_name="MockSat-2"),
    ]


def test_update_satellite_catalog_maps_two_outputs_correctly(celestrak_outputs):
    fetched_at = datetime(2026, 2, 24, 12, 0, 0, tzinfo=UTC)

    outputs = [
        create_celestrak_output(
            satellite_id="12345",
            satellite_name="MockSat-1",
            fetched_at=fetched_at,
            next_positions=[create_position(latitude=1.0, longitude=2.0)],
        ),
        create_celestrak_output(
            satellite_id="67890",
            satellite_name="MockSat-2",
            fetched_at=fetched_at,
            next_positions=[create_position(latitude=3.0, longitude=4.0)],
        ),
    ]

    mock_celestrak = MagicMock()
    mock_repo = MagicMock()
    mock_celestrak.calculate_positions.return_value = outputs

    service = SatelliteCatalogService(celestrak_service=mock_celestrak, repository=mock_repo)
    service.update_satellite_catalog()

    mock_repo.upsert_positions_to_db.assert_called_once()
    positions = mock_repo.upsert_positions_to_db.call_args.args[0]

    assert [p.satellite_id for p in positions] == ["12345", "67890"]
    assert [p.satellite_name for p in positions] == ["MockSat-1", "MockSat-2"]
    assert all(p.fetched_at == fetched_at for p in positions)

    assert positions[0].next_positions[0].latitude == 1.0
    assert positions[0].next_positions[0].longitude == 2.0
    assert positions[1].next_positions[0].latitude == 3.0
    assert positions[1].next_positions[0].longitude == 4.0
