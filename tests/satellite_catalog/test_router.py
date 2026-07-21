import asyncio
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi import HTTPException

from app.models import SatelliteCatalogStatus
from app.satellite_catalog.router import create_satellite_catalog_router


class StubSatelliteCatalogService:
    def get_catalog_status(self) -> SatelliteCatalogStatus:
        return SatelliteCatalogStatus(
            satellite_count=157,
            latest_tle_fetched_at=datetime(2026, 7, 21, 12, 0, tzinfo=UTC),
            source="celestrak",
        )


class FailingSatelliteCatalogService:
    def get_catalog_status(self) -> SatelliteCatalogStatus:
        raise RuntimeError("database unavailable")


def test_get_catalog_status_returns_catalog_status() -> None:
    router = create_satellite_catalog_router(service=StubSatelliteCatalogService())
    endpoint = _get_route_endpoint(router, "/satellite_catalog/status")

    response = asyncio.run(endpoint())

    assert response == SatelliteCatalogStatus(
        satellite_count=157,
        latest_tle_fetched_at=datetime(2026, 7, 21, 12, 0, tzinfo=UTC),
        source="celestrak",
    )


def test_get_catalog_status_returns_503_when_status_cannot_be_read() -> None:
    router = create_satellite_catalog_router(service=FailingSatelliteCatalogService())
    endpoint = _get_route_endpoint(router, "/satellite_catalog/status")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(endpoint())

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Could not retrieve satellite catalog status"


def _get_route_endpoint(router: Any, path: str) -> Any:
    return next(route.endpoint for route in router.routes if route.path == path)
