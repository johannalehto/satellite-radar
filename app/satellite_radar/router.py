from fastapi import APIRouter

router = APIRouter()


# @router.get("/satellite_radar/get_satellites_now/{lat}/{lon}")
# async def get_satellites_now(lat: float, lon: float) -> SatellitesNowResponse | None:
#     try:
#         satellites_now = get_satellites_above(lat, lon)
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None
#     return satellites_now
