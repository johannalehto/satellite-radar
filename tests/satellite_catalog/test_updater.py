from unittest.mock import MagicMock

import pytest

from app.satellite_catalog.updater import run_update


def test_run_update_calls_service_update() -> None:
    mock_service = MagicMock()

    run_update(service=mock_service)

    mock_service.update_satellite_catalog.assert_called_once_with()


def test_run_update_raises_exception() -> None:
    mock_service = MagicMock()
    mock_service.update_satellite_catalog.side_effect = RuntimeError("error")

    with pytest.raises(RuntimeError, match="error"):
        run_update(service=mock_service)
