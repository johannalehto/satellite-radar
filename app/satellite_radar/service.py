import logging
from datetime import UTC, datetime, timedelta
from typing import Final, Protocol

from app.models import (
    RadarTrackPoint,
    SatelliteCatalogItem,
    SatelliteRadarItem,
)
from app.satellite_radar.builders import build_satellite_radar_item
from app.satellite_radar.errors import SatelliteRadarCatalogUnavailableError
from app.satellite_radar.track_calculator import (
    SatelliteTrackCalculator,
    SkyfieldSatelliteTrackCalculator,
)

logger = logging.getLogger(__name__)

DEFAULT_MINUTES_BEFORE: Final[int] = 5
DEFAULT_MINUTES_AFTER: Final[int] = 5
DEFAULT_STEP_SECONDS: Final[int] = 30
DEFAULT_SATELLITE_LIMIT: Final[int] = 10
MIN_VISIBLE_ELEVATION_DEGREES: Final[float] = 10.0


class SatelliteCatalogReader(Protocol):
    def get_all_satellites(self) -> list[SatelliteCatalogItem]: ...


class SatelliteRadarService:
    def __init__(
        self,
        satellite_catalog: SatelliteCatalogReader,
        track_calculator: SatelliteTrackCalculator | None = None,
    ):
        self.satellite_catalog = satellite_catalog
        self.track_calculator = track_calculator or SkyfieldSatelliteTrackCalculator()

    @staticmethod
    def get_visible_track(track: list[RadarTrackPoint]) -> list[RadarTrackPoint]:
        # TODO: add sun related visibility filtering
        return [point for point in track if point.elevation_deg >= MIN_VISIBLE_ELEVATION_DEGREES]

    def _build_satellite_radar_item(
        self,
        item: SatelliteCatalogItem,
        *,
        lat: float,
        lon: float,
        start_time: datetime,
        total_minutes: int,
        step_seconds: int,
    ) -> SatelliteRadarItem | None:
        track = self.track_calculator.calculate_track(
            item,
            observer_lat=lat,
            observer_lon=lon,
            start_time=start_time,
            total_minutes=total_minutes,
            step_seconds=step_seconds,
        )

        visible_track = self.get_visible_track(track)

        if not visible_track:
            return None

        return build_satellite_radar_item(item, visible_track)

    def get_visible_satellites(
        self,
        lat: float,
        lon: float,
        *,
        minutes_before: int = DEFAULT_MINUTES_BEFORE,
        minutes_after: int = DEFAULT_MINUTES_AFTER,
        step_seconds: int = DEFAULT_STEP_SECONDS,
        limit: int = DEFAULT_SATELLITE_LIMIT,
        now: datetime | None = None,
    ) -> list[SatelliteRadarItem]:
        now = now or datetime.now(UTC)

        start_time = now - timedelta(minutes=minutes_before)
        total_minutes = minutes_before + minutes_after

        try:
            catalog_items = self.satellite_catalog.get_all_satellites()
        except Exception as e:  # noqa: BLE001
            raise SatelliteRadarCatalogUnavailableError(
                "Could not retrieve satellite catalog"
            ) from e

        visible_satellites: list[SatelliteRadarItem] = []

        for item in catalog_items:
            try:
                radar_item = self._build_satellite_radar_item(
                    item,
                    lat=lat,
                    lon=lon,
                    start_time=start_time,
                    total_minutes=total_minutes,
                    step_seconds=step_seconds,
                )
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Skipping satellite %s because radar calculation failed",
                    item.satellite_id,
                )
                continue

            if radar_item is None:
                continue

            visible_satellites.append(radar_item)

        sorted_satellites = sorted(
            visible_satellites,
            key=lambda satellite: satellite.visibility.visible_until,
        )

        return sorted_satellites[:limit]
