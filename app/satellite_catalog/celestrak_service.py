import logging
from typing import Final

from skyfield.api import load
from datetime import datetime, timedelta

from skyfield.timelib import Time

from app.config import CELESTRAK_100_BRIGHTEST_URL
from app.models import CelestrakSatelliteOutput, Position

logger = logging.getLogger(__name__)

DURATION_HOURS: Final[int] = 2
INTERVAL_MINUTES: Final[int] = 15
MAX_ALTITUDE_KM: Final[float] = 2000.0

class CelestrakService:
    def __init__(self):
        self.stations_url = CELESTRAK_100_BRIGHTEST_URL
        self.satellites = load.tle_file(self.stations_url)
        self.ts = load.timescale()
        self.t = self.ts.now()  # current time as an astronomical time object

        self.duration_hours = DURATION_HOURS
        self.interval_minutes = INTERVAL_MINUTES

    def generate_time_intervals(self, start_time: datetime) -> list[Time]:
        intervals = []
        for minute in range(0, self.duration_hours * 60, self.interval_minutes):
            t = start_time + timedelta(minutes=minute)
            intervals.append(self.ts.utc(t.year, t.month, t.day, t.hour, t.minute, t.second))
        return intervals

    @staticmethod
    def create_position(subpoint, timestamp: Time) -> Position:
        geographic_position = subpoint.subpoint()
        return Position(
            timestamp=timestamp.utc_datetime(),
            latitude=geographic_position.latitude.degrees,
            longitude=geographic_position.longitude.degrees,
            altitude_km=geographic_position.elevation.km
        )

    def calculate_positions(self) -> list[CelestrakSatelliteOutput]:

        start_time = self.t.utc_datetime()
        if isinstance(start_time, tuple):
            start_time = datetime(*start_time)

        time_intervals = self.generate_time_intervals(start_time=start_time)
        all_celetrak_satellites = []

        for satellite in self.satellites:
            subpoints = [satellite.at(t) for t in time_intervals]
            positions = []
            for subpoint, timestamp in zip(subpoints, time_intervals):
                positions.append(self.create_position(subpoint, timestamp))

            all_celetrak_satellites.append(CelestrakSatelliteOutput(
                satellite_id=satellite.model.satnum_str,
                satellite_name=satellite.name,
                next_positions=positions
            ))
        logger.info(f"DEBUG: Added Celetrak satellites: {[sat.satellite_name for sat in all_celetrak_satellites]}")
        return all_celetrak_satellites

