import logging
import math
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final

from skyfield.api import load
from skyfield.sgp4lib import EarthSatellite
from skyfield.timelib import Time

from app.config import CELESTRAK_100_BRIGHTEST_URL
from app.models import CelestrakSatelliteOutput, Position, RawTLEEntry, TLEData, TLEParsed

logger = logging.getLogger(__name__)

CELESTRAK_GROUP: Final[str] = "visual"
CELESTRAK_SOURCE: Final[str] = "celestrak"

DURATION_HOURS: Final[int] = 26
INTERVAL_MINUTES: Final[int] = 60
MAX_ALTITUDE_KM: Final[float] = 2000.0


class CelestrakService:
    def __init__(self, lines_loader: Callable[[], list[str]] | None = None):
        self.stations_url = CELESTRAK_100_BRIGHTEST_URL
        self.satellites = load.tle_file(self.stations_url)
        self.ts = load.timescale()
        self.t = self.ts.now()  # current time as an astronomical time object

        self._lines_loader = lines_loader or self._load_celestrak_lines

        self.duration_hours = DURATION_HOURS
        self.interval_minutes = INTERVAL_MINUTES

    @staticmethod
    def _build_tle_parsed(satellite: EarthSatellite) -> TLEParsed:
        model = satellite.model

        return TLEParsed(
            epoch=satellite.epoch.utc_datetime(),
            inclination_deg=math.degrees(float(model.inclo)),
            raan_deg=math.degrees(float(model.nodeo)),
            eccentricity=float(model.ecco),
            mean_motion_rev_per_day=float(model.no_kozai * 1440.0 / (2.0 * math.pi)),
            drag_term_bstar=float(model.bstar),
        )

    def _load_celestrak_lines(self) -> list[str]:
        with load.open(self.stations_url) as file_obj:
            return [line.decode("utf-8").strip() for line in file_obj if line.strip()]

    @staticmethod
    def _parse_raw_tle_entries(lines: list[str]) -> list[RawTLEEntry]:
        if len(lines) % 3 != 0:
            raise ValueError(
                "Invalid CelesTrak TLE payload: expected name + 2 TLE lines per satellite"
            )

        entries: list[RawTLEEntry] = []

        for index in range(0, len(lines), 3):
            name = lines[index]
            line1 = lines[index + 1]
            line2 = lines[index + 2]

            if not line1.startswith("1 ") or not line2.startswith("2 "):
                logger.warning(
                    "Skipping invalid TLE for satellite %s",
                    name,
                )
                continue

            entries.append(RawTLEEntry(name=name, line1=line1, line2=line2))

        return entries

    def fetch_tles(self) -> list[CelestrakSatelliteOutput]:
        fetched_at = self.t.utc_datetime()
        raw_lines = self._lines_loader()
        raw_entries = self._parse_raw_tle_entries(raw_lines)

        all_celestrak_satellites: list[CelestrakSatelliteOutput] = []

        for entry in raw_entries:
            satellite = EarthSatellite(entry.line1, entry.line2, entry.name, self.ts)

            all_celestrak_satellites.append(
                CelestrakSatelliteOutput(
                    satellite_id=satellite.model.satnum_str,
                    satellite_name=entry.name,
                    fetched_at=fetched_at,
                    tle=TLEData(
                        line1=entry.line1,
                        line2=entry.line2,
                        group=CELESTRAK_GROUP,
                        source=CELESTRAK_SOURCE,
                        fetched_at=fetched_at,
                        parsed=self._build_tle_parsed(satellite),
                    ),
                )
            )

        satellite_names = [sat.satellite_name for sat in all_celestrak_satellites]
        logger.info("DEBUG: Added Celestrak satellites: %s", satellite_names)

        return all_celestrak_satellites

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
            altitude_km=geographic_position.elevation.km,
        )

    def calculate_positions(self) -> list[CelestrakSatelliteOutput]:

        start_time = self.t.utc_datetime()
        if isinstance(start_time, tuple):
            start_time = datetime(*start_time)

        time_intervals = self.generate_time_intervals(start_time=start_time)
        all_celestrak_satellites = []

        for satellite in self.satellites:
            subpoints = [satellite.at(t) for t in time_intervals]
            positions = []
            for subpoint, timestamp in zip(subpoints, time_intervals, strict=False):
                positions.append(self.create_position(subpoint, timestamp))

            all_celestrak_satellites.append(
                CelestrakSatelliteOutput(
                    satellite_id=satellite.model.satnum_str,
                    satellite_name=satellite.name,
                    next_positions=positions,
                    fetched_at=self.t.utc_datetime(),
                )
            )
        satellite_names = [sat.satellite_name for sat in all_celestrak_satellites]

        logger.info(f"DEBUG: Added Celestrak satellites: {satellite_names}")
        return all_celestrak_satellites
