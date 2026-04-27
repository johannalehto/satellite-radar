from datetime import UTC, datetime, timedelta

from skyfield.api import EarthSatellite, wgs84

from app.models import RadarSatelliteResult, RadarTrackPoint, SatelliteCatalogItem
from app.satellite_catalog.service import SatelliteCatalogService

DEFAULT_MINUTES_AHEAD = 20
DEFAULT_STEP_SECONDS = 30
DEFAULT_SATELLITE_LIMIT = 10
MIN_VISIBLE_ELEVATION_DEGREE = 10.0


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
        minutes_ahead: int,
        step_seconds: int,
    ) -> list[RadarTrackPoint]:
        if start_time.tzinfo is None:
            raise ValueError("start_time must be timezone-aware")

        ts = satellite.ts
        observer = wgs84.latlon(observer_lat, observer_lon)

        points: list[RadarTrackPoint] = []
        total_steps = (minutes_ahead * 60) // step_seconds + 1

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
    def is_satellite_visible(track: list[RadarTrackPoint]) -> bool:
        return any(point.elevation_deg >= MIN_VISIBLE_ELEVATION_DEGREE for point in track)

    @staticmethod
    def is_satellite_visible_now(track: list[RadarTrackPoint]) -> bool:
        return bool(track) and track[0].elevation_deg >= MIN_VISIBLE_ELEVATION_DEGREE

    @staticmethod
    def get_max_elevation(track: list[RadarTrackPoint]) -> float:
        return max(point.elevation_deg for point in track)

    @staticmethod
    def get_visible_track(track: list[RadarTrackPoint]) -> list[RadarTrackPoint]:
        return [point for point in track if point.elevation_deg >= MIN_VISIBLE_ELEVATION_DEGREE]

    def get_visible_satellites(
        self,
        lat: float,
        lon: float,
        *,
        minutes_ahead: int = DEFAULT_MINUTES_AHEAD,
        step_seconds: int = DEFAULT_STEP_SECONDS,
        limit: int | None = DEFAULT_SATELLITE_LIMIT,
        now: datetime | None = None,
    ) -> list[RadarSatelliteResult]:
        now = now or datetime.now(UTC)

        catalog_items = self.satellite_catalog.get_all_satellites()

        visible_satellites: list[RadarSatelliteResult] = []

        for item in catalog_items:
            satellite = self.build_earth_satellite(item)
            track = self.calculate_satellite_track(
                satellite,
                observer_lat=lat,
                observer_lon=lon,
                start_time=now,
                minutes_ahead=minutes_ahead,
                step_seconds=step_seconds,
            )

            visible_track = self.get_visible_track(track)

            if not visible_track:
                continue

            visible_satellites.append(
                RadarSatelliteResult(
                    satellite_id=item.satellite_id,
                    satellite_name=item.satellite_name,
                    visible_now=self.is_satellite_visible_now(track),
                    max_elevation_deg=self.get_max_elevation(track),
                    track=visible_track,
                )
            )

        if limit is not None:
            return visible_satellites[:limit]

        return visible_satellites
