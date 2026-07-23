from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from skyfield.api import load

from app.models import SatelliteObjectType, SatelliteTLEUpdate
from app.satellite_catalog.celestrak_service import CelestrakService, RawTLEEntry
from tests.factory import create_earth_satellite


@pytest.fixture
def timescale():
    ts = load.timescale()
    return ts


@pytest.fixture
def satellites():
    return [create_earth_satellite()]


def test_parse_raw_tle_entries_returns_entries_for_valid_lines() -> None:
    lines = [
        "ATLAS CENTAUR 2",
        "1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        "2 00694  30.3551  20.9180 0560095 134.0904 230.7205 14.08963668 62697",
        "ISS (ZARYA)",
        "1 25544U 98067A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        "2 25544  51.6416  20.9180 0005217 134.0904 230.7205 15.49859268 62697",
    ]

    entries = CelestrakService._parse_raw_tle_entries(lines)

    assert len(entries) == 2
    assert entries[0] == RawTLEEntry(
        name="ATLAS CENTAUR 2",
        line1="1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        line2="2 00694  30.3551  20.9180 0560095 134.0904 230.7205 14.08963668 62697",
    )
    assert entries[1].name == "ISS (ZARYA)"


def test_parse_raw_tle_entries_skips_invalid_tle_lines() -> None:
    lines = [
        "ATLAS CENTAUR 2",
        "1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        "2 00694  30.3551  20.9180 0560095 134.0904 230.7205 14.08963668 62697",
        "BROKEN SAT",
        "X not-a-real-line1",
        "Y not-a-real-line2",
    ]

    entries = CelestrakService._parse_raw_tle_entries(lines)

    assert len(entries) == 1
    assert entries[0].name == "ATLAS CENTAUR 2"


def test_parse_raw_tle_entries_raises_for_invalid_payload_shape() -> None:
    lines = [
        "ATLAS CENTAUR 2",
        "1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
    ]

    with pytest.raises(
        ValueError,
        match="Invalid CelesTrak TLE payload: expected name \\+ 2 TLE lines per satellite",
    ):
        CelestrakService._parse_raw_tle_entries(lines)


def test_fetch_tles_returns_outputs_with_tle_data() -> None:
    raw_lines = [
        "ATLAS CENTAUR 2",
        "1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        "2 00694  30.3551  20.9180 0560095 134.0904 230.7205 14.08963668 62697",
    ]

    def loader() -> list[str]:
        return list(raw_lines)

    service = CelestrakService(lines_loader=lambda: raw_lines)

    service.t = MagicMock()
    service.t.utc_datetime.return_value = datetime(2026, 2, 25, 12, 0, tzinfo=UTC)

    results = service.fetch_tles()

    assert len(results) == 1
    assert isinstance(results[0], SatelliteTLEUpdate)
    assert results[0].satellite_name == "ATLAS CENTAUR 2"
    assert results[0].satellite_id == "00694"

    assert results[0].tle is not None
    assert results[0].tle.line1.startswith("1 00694U")
    assert results[0].tle.line2.startswith("2 00694")
    assert results[0].tle.group == "visual"
    assert results[0].tle.source == "celestrak"
    assert results[0].tle.fetched_at == datetime(2026, 2, 25, 12, 0, tzinfo=UTC)

    assert results[0].tle.parsed.inclination_deg == pytest.approx(30.3551)
    assert results[0].tle.parsed.raan_deg == pytest.approx(20.9180)


def test_fetch_tles_skips_invalid_entries_and_returns_valid_ones() -> None:
    raw_lines = [
        "ATLAS CENTAUR 2",
        "1 00694U 63047A   24314.62518451  .00007658  00000+0  95096-3 0  9992",
        "2 00694  30.3551  20.9180 0560095 134.0904 230.7205 14.08963668 62697",
        "BROKEN SAT",
        "X not-a-real-line1",
        "Y not-a-real-line2",
    ]

    service = CelestrakService(lines_loader=lambda: raw_lines)

    results = service.fetch_tles()

    assert len(results) == 1
    assert results[0].satellite_name == "ATLAS CENTAUR 2"


def test_fetch_satcat_metadata_returns_metadata_updates() -> None:
    raw_records = [
        {
            "NORAD_CAT_ID": 694,
            "OBJECT_NAME": "ATLAS CENTAUR 2",
            "OBJECT_TYPE": "R/B",
            "OPS_STATUS_CODE": "D",
            "OWNER": "US",
            "LAUNCH_DATE": "1963-11-27",
            "LAUNCH_SITE": "AFETR",
        }
    ]

    service = CelestrakService(
        lines_loader=lambda: [],
        satcat_loader=lambda: raw_records,
    )
    service.t = MagicMock()
    service.t.utc_datetime.return_value = datetime(2026, 2, 25, 12, 0, tzinfo=UTC)

    results = service.fetch_satcat_metadata()

    assert len(results) == 1
    assert results[0].satellite_id == "00694"
    assert results[0].satellite_name == "ATLAS CENTAUR 2"
    assert results[0].metadata.source == "celestrak"
    assert results[0].metadata.fetched_at == datetime(2026, 2, 25, 12, 0, tzinfo=UTC)
    assert results[0].metadata.owner is not None
    assert results[0].metadata.owner.code == "US"
    assert results[0].metadata.owner.name == "United States"
    assert results[0].metadata.object_type == SatelliteObjectType.ROCKET_BODY
    assert results[0].metadata.launch is not None
    assert results[0].metadata.launch.date == datetime(1963, 11, 27, tzinfo=UTC).date()
    assert results[0].metadata.launch.site is not None
    assert results[0].metadata.launch.site.code == "AFETR"
    assert results[0].metadata.launch.site.name == "Cape Canaveral Space Force Station"


def test_fetch_satcat_metadata_skips_invalid_records() -> None:
    raw_records = [
        {
            "NORAD_CAT_ID": 694,
            "OBJECT_NAME": "ATLAS CENTAUR 2",
            "LAUNCH_DATE": "1963-11-27",
        },
        {
            "NORAD_CAT_ID": 695,
            "OBJECT_NAME": "BROKEN SAT",
            "LAUNCH_DATE": "not-a-date",
        },
    ]

    service = CelestrakService(
        lines_loader=lambda: [],
        satcat_loader=lambda: raw_records,
    )

    results = service.fetch_satcat_metadata()

    assert len(results) == 1
    assert results[0].satellite_id == "00694"


def test_fetch_satcat_metadata_converts_empty_optional_strings_to_none() -> None:
    raw_records = [
        {
            "NORAD_CAT_ID": 694,
            "OBJECT_NAME": "ATLAS CENTAUR 2",
            "OWNER": "",
            "OBJECT_TYPE": "",
            "LAUNCH_SITE": "",
        }
    ]

    service = CelestrakService(
        lines_loader=lambda: [],
        satcat_loader=lambda: raw_records,
    )

    results = service.fetch_satcat_metadata()

    assert len(results) == 1
    assert results[0].metadata.owner is None
    assert results[0].metadata.object_type is None
    assert results[0].metadata.launch is None


def test_fetch_satcat_metadata_maps_owner_codes_to_readable_names() -> None:
    raw_records = [
        {
            "NORAD_CAT_ID": 694,
            "OBJECT_NAME": "CHINA SAT",
            "OWNER": "PRC",
        },
        {
            "NORAD_CAT_ID": 695,
            "OBJECT_NAME": "TAIWAN SAT",
            "OWNER": "ROC",
        },
    ]

    service = CelestrakService(
        lines_loader=lambda: [],
        satcat_loader=lambda: raw_records,
    )

    results = service.fetch_satcat_metadata()

    assert results[0].metadata.owner is not None
    assert results[0].metadata.owner.name == "China"
    assert results[1].metadata.owner is not None
    assert results[1].metadata.owner.name == "Taiwan"


def test_fetch_satcat_metadata_maps_launch_site_codes_to_readable_names() -> None:
    raw_records = [
        {
            "NORAD_CAT_ID": 694,
            "OBJECT_NAME": "ATLAS CENTAUR 2",
            "LAUNCH_SITE": "TYMSC",
        }
    ]

    service = CelestrakService(
        lines_loader=lambda: [],
        satcat_loader=lambda: raw_records,
    )

    results = service.fetch_satcat_metadata()

    assert results[0].metadata.launch is not None
    assert results[0].metadata.launch.site is not None
    assert results[0].metadata.launch.site.code == "TYMSC"
    assert results[0].metadata.launch.site.name == "Taiyuan Satellite Launch Center"
