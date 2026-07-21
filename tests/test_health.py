import asyncio
from typing import Any

from app.health import create_health_router


def test_health_returns_ok() -> None:
    router = create_health_router()
    endpoint = _get_route_endpoint(router, "/health")

    assert asyncio.run(endpoint()) == {"status": "ok"}


def _get_route_endpoint(router: Any, path: str) -> Any:
    return next(route.endpoint for route in router.routes if route.path == path)
