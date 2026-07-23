import json
import logging
import math
from collections.abc import Callable
from datetime import date
from typing import Any, Final

from pydantic import ValidationError
from skyfield.api import load
from skyfield.sgp4lib import EarthSatellite

from app.config import CELESTRAK_100_BRIGHTEST_URL, CELESTRAK_SATCAT_URL
from app.models import (
    RawSatcatEntry,
    RawTLEEntry,
    SatelliteMetadata,
    SatelliteMetadataUpdate,
    SatelliteTLEUpdate,
    TLEData,
    TLEParsed,
)

logger = logging.getLogger(__name__)

CELESTRAK_GROUP: Final[str] = "visual"
CELESTRAK_SOURCE: Final[str] = "celestrak"


class CelestrakService:
    def __init__(
        self,
        lines_loader: Callable[[], list[str]] | None = None,
        satcat_loader: Callable[[], list[dict[str, Any]]] | None = None,
    ):
        self.stations_url = CELESTRAK_100_BRIGHTEST_URL
        self.satcat_url = CELESTRAK_SATCAT_URL
        self.ts = load.timescale()
        self.t = self.ts.now()  # current time as an astronomical time object

        self._lines_loader = lines_loader or self._load_celestrak_lines
        self._satcat_loader = satcat_loader or self._load_satcat_records

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

    def _load_satcat_records(self) -> list[dict[str, Any]]:
        with load.open(self.satcat_url) as file_obj:
            return json.load(file_obj)

    @staticmethod
    def _parse_optional_date(value: str | None) -> date | None:
        if not value:
            return None

        return date.fromisoformat(value)

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

    def fetch_tles(self) -> list[SatelliteTLEUpdate]:
        fetched_at = self.t.utc_datetime()
        raw_lines = self._lines_loader()
        raw_entries = self._parse_raw_tle_entries(raw_lines)

        satellites_with_tle_update: list[SatelliteTLEUpdate] = []

        for entry in raw_entries:
            satellite = EarthSatellite(entry.line1, entry.line2, entry.name, self.ts)

            satellites_with_tle_update.append(
                SatelliteTLEUpdate(
                    satellite_id=satellite.model.satnum_str,
                    satellite_name=entry.name,
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

        satellite_names = [sat.satellite_name for sat in satellites_with_tle_update]
        logger.info("DEBUG: Added Celestrak satellites: %s", satellite_names)

        return satellites_with_tle_update

    def fetch_satcat_metadata(self) -> list[SatelliteMetadataUpdate]:
        fetched_at = self.t.utc_datetime()
        raw_records = self._satcat_loader()

        metadata_updates: list[SatelliteMetadataUpdate] = []

        for raw_record in raw_records:
            try:
                satcat_entry = RawSatcatEntry.model_validate(raw_record)

                metadata_updates.append(
                    SatelliteMetadataUpdate(
                        satellite_id=str(satcat_entry.satellite_id).zfill(5),
                        satellite_name=satcat_entry.satellite_name,
                        metadata=SatelliteMetadata(
                            source=CELESTRAK_SOURCE,
                            fetched_at=fetched_at,
                            owner=satcat_entry.owner or None,
                            object_type=satcat_entry.object_type or None,
                            launch_date=self._parse_optional_date(satcat_entry.launch_date),
                            launch_site=satcat_entry.launch_site or None,
                        ),
                    ),
                )
            except (ValidationError, ValueError):
                logger.warning("Skipping invalid CelesTrak SATCAT record: %s", raw_record)
                continue

        return metadata_updates
