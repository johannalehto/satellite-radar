import logging
from datetime import UTC, datetime, timedelta
from typing import Final

from skyfield.api import EarthSatellite, wgs84

from app.models import (
    RadarTrackPoint,
    SatelliteCatalogItem,
    SatelliteInfo,
    SatellitePassPoint,
    SatelliteRadarItem,
    SatelliteVisibility,
)
from app.satellite_catalog.service import SatelliteCatalogService
from app.satellite_radar.errors import SatelliteRadarCatalogUnavailableError

logger = logging.getLogger(__name__)

DEFAULT_MINUTES_BEFORE: Final[int] = 5
DEFAULT_MINUTES_AFTER: Final[int] = 5
DEFAULT_STEP_SECONDS: Final[int] = 30
DEFAULT_SATELLITE_LIMIT: Final[int] = 10
MIN_VISIBLE_ELEVATION_DEGREES: Final[float] = 10.0


class SatelliteRadarService:
    def __init__(self, satellite_catalog: SatelliteCatalogService):
        self.satellite_catalog = satellite_catalog

    @staticmethod
    def build_earth_satellite(catalog_item: SatelliteCatalogItem) -> EarthSatellite:
        return EarthSatellite(
            catalog_item.tle.line1,
            catalog_item.tle.line2,
            catalog_item.satellite_name,
        )

    @staticmethod
    def calculate_satellite_track(
        satellite: EarthSatellite,
        *,
        observer_lat: float,
        observer_lon: float,
        start_time: datetime,
        total_minutes: int,
        step_seconds: int,
    ) -> list[RadarTrackPoint]:
        if start_time.tzinfo is None:
            raise ValueError("start_time must be timezone-aware")

        ts = satellite.ts
        observer = wgs84.latlon(observer_lat, observer_lon)

        points: list[RadarTrackPoint] = []
        total_steps = (total_minutes * 60) // step_seconds + 1

        for step in range(total_steps):
            point_time = start_time + timedelta(seconds=step * step_seconds)
            t = ts.from_datetime(point_time.astimezone(UTC))

            topocentric = (satellite - observer).at(t)
            alt, az, distance = topocentric.altaz()

            points.append(
                RadarTrackPoint(
                    timestamp=point_time,
                    azimuth_deg=az.degrees,
                    elevation_deg=alt.degrees,
                    distance_km=distance.km,
                )
            )

        return points

    @staticmethod
    def get_max_elevation(track: list[RadarTrackPoint]) -> float:
        return max(point.elevation_deg for point in track)

    @staticmethod
    def azimuth_to_direction(azimuth_deg: float) -> str:
        directions = [
            "N",
            "NE",
            "E",
            "SE",
            "S",
            "SW",
            "W",
            "NW",
        ]
        index = round(azimuth_deg / 45) % 8
        return directions[index]

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
        satellite = self.build_earth_satellite(item)
        track = self.calculate_satellite_track(
            satellite,
            observer_lat=lat,
            observer_lon=lon,
            start_time=start_time,
            total_minutes=total_minutes,
            step_seconds=step_seconds,
        )

        visible_track = self.get_visible_track(track)

        if not visible_track:
            return None

        start_azimuth_deg = visible_track[0].azimuth_deg
        end_azimuth_deg = visible_track[-1].azimuth_deg

        return SatelliteRadarItem(
            info=SatelliteInfo(
                satellite_id=item.satellite_id,
                satellite_name=item.satellite_name,
            ),
            visibility=SatelliteVisibility(
                visible_from=visible_track[0].timestamp,
                visible_until=visible_track[-1].timestamp,
                max_elevation_deg=self.get_max_elevation(visible_track),
            ),
            start=SatellitePassPoint(
                azimuth_deg=start_azimuth_deg,
                direction=self.azimuth_to_direction(start_azimuth_deg),
            ),
            end=SatellitePassPoint(
                azimuth_deg=end_azimuth_deg,
                direction=self.azimuth_to_direction(end_azimuth_deg),
            ),
            track=visible_track,
        )

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
