from pathlib import Path


def test_debug_page_references_satellite_radar_response_fields() -> None:
    html = Path("debug/satellites-now.html").read_text()

    required_fields = [
        "pass.info.satellite_name",
        "pass.info.satellite_id",
        "pass.visibility.visible_from",
        "pass.visibility.visible_until",
        "pass.visibility.max_elevation_deg",
        "pass.start.direction",
        "pass.end.direction",
        "pass.track",
    ]

    for field in required_fields:
        assert field in html
