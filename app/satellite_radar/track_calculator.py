from datetime import UTC, datetime, timedelta
from typing import Protocol

from skyfield.api import EarthSatellite, wgs84

from app.models import RadarTrackPoint, SatelliteCatalogItem


class SatelliteTrackCalculator(Protocol):
    def calculate_track(
        self,
        catalog_item: SatelliteCatalogItem,
        *,
        observer_lat: float,
        observer_lon: float,
        start_time: datetime,
        total_minutes: int,
        step_seconds: int,
    ) -> list[RadarTrackPoint]: ...


class SkyfieldSatelliteTrackCalculator:
    def calculate_track(
        self,
        catalog_item: SatelliteCatalogItem,
        *,
        observer_lat: float,
        observer_lon: float,
        start_time: datetime,
        total_minutes: int,
        step_seconds: int,
    ) -> list[RadarTrackPoint]:
        if start_time.tzinfo is None:
            raise ValueError("start_time must be timezone-aware")

        satellite = EarthSatellite(
            catalog_item.tle.line1,
            catalog_item.tle.line2,
            catalog_item.satellite_name,
        )
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
