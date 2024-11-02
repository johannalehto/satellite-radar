from pydantic import BaseModel


class Satellite (BaseModel):
    id: int
    name: str
    country_of_origin: str | None
    launched_since: str
  #  description: str | None
    direction: str | None
    visible_until: str | None

class SatellitesNowResponse (BaseModel):
    location: tuple[float, float]
    satellites: list[Satellite]