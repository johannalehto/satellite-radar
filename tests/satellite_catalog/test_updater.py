from unittest.mock import MagicMock

import pytest

from app.satellite_catalog.updater import run_catalog_update, run_tle_update


def test_run_catalog_update_calls_service_tle_and_metadata_updates() -> None:
    mock_service = MagicMock()

    run_catalog_update(service=mock_service)

    mock_service.update_satellite_catalog_with_tle_data.assert_called_once_with()
    mock_service.update_satellite_catalog_with_metadata.assert_called_once_with()


def test_run_tle_update_calls_service_tle_update() -> None:
    mock_service = MagicMock()

    run_tle_update(service=mock_service)

    mock_service.update_satellite_catalog_with_tle_data.assert_called_once_with()


def test_run_tle_update_raises_exception() -> None:
    mock_service = MagicMock()
    mock_service.update_satellite_catalog_with_tle_data.side_effect = RuntimeError("error")

    with pytest.raises(RuntimeError, match="error"):
        run_tle_update(service=mock_service)


def test_run_catalog_update_raises_exception() -> None:
    mock_service = MagicMock()
    mock_service.update_satellite_catalog_with_metadata.side_effect = RuntimeError("error")

    with pytest.raises(RuntimeError, match="error"):
        run_catalog_update(service=mock_service)
