from models import SatellitesNowResponse, Satellite


def api_response_to_satellites_now_response(response: dict, lat: float, lon: float) -> SatellitesNowResponse:
    return SatellitesNowResponse(
        location=(lat, lon),
        satellites=[
            Satellite(
                id=sat["satid"],
                name=sat["satname"],
                country_of_origin=sat.get("country", None),
                launched_since=sat["launchDate"],
                direction=sat.get("direction", None),
                visible_until=sat.get("visibleUntil", None),
            )
            for sat in response["above"]
            if 160 <= sat["satalt"] <= 2000  # Focus on low Earth orbit satellites
        ],
    )