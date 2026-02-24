from unittest.mock import MagicMock

import pytest

from app.satellite_catalog.service import SatelliteCatalogService
from tests.factory import create_celestrak_output


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
