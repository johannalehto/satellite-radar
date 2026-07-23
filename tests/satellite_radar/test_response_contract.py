from tests.factory import create_radar_result


def test_satellite_radar_item_response_shape() -> None:
    response = create_radar_result().model_dump()

    assert set(response) == {"info", "visibility", "start", "end", "track"}
    assert set(response["info"]) == {
        "satellite_id",
        "satellite_name",
        "owner",
        "object_type",
        "launch_date",
        "launch_site",
    }
    assert set(response["visibility"]) == {
        "visible_from",
        "visible_until",
        "max_elevation_deg",
    }
    assert set(response["start"]) == {"azimuth_deg", "direction"}
    assert set(response["end"]) == {"azimuth_deg", "direction"}
