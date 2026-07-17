from app.models import (
    RadarTrackPoint,
    SatelliteCatalogItem,
    SatelliteInfo,
    SatellitePassPoint,
    SatelliteRadarItem,
    SatelliteVisibility,
)


def get_max_elevation(track: list[RadarTrackPoint]) -> float:
    return max(point.elevation_deg for point in track)


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


def build_satellite_radar_item(
    catalog_item: SatelliteCatalogItem,
    visible_track: list[RadarTrackPoint],
) -> SatelliteRadarItem:
    start_azimuth_deg = visible_track[0].azimuth_deg
    end_azimuth_deg = visible_track[-1].azimuth_deg

    return SatelliteRadarItem(
        info=SatelliteInfo(
            satellite_id=catalog_item.satellite_id,
            satellite_name=catalog_item.satellite_name,
        ),
        visibility=SatelliteVisibility(
            visible_from=visible_track[0].timestamp,
            visible_until=visible_track[-1].timestamp,
            max_elevation_deg=get_max_elevation(visible_track),
        ),
        start=SatellitePassPoint(
            azimuth_deg=start_azimuth_deg,
            direction=azimuth_to_direction(start_azimuth_deg),
        ),
        end=SatellitePassPoint(
            azimuth_deg=end_azimuth_deg,
            direction=azimuth_to_direction(end_azimuth_deg),
        ),
        track=visible_track,
    )
