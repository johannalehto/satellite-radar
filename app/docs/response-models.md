
Test response for web
```bash
info:
  satellite_id: str
  satellite_name: str
  country: str | None
  info_text: str | None

visibility:
  visible_from: datetime
  visible_until: datetime
  max_elevation_deg: float

start:
  azimuth_deg: float
  direction: str

end:
  azimuth_deg: float
  direction: str

track: list[RadarTrackPoint]

```

```bash
Approaching

id: 25544
name: ISS (ZARYA)

towards: North-West 45°
visible: 00:20

origin: China
orbitting since: 1998-11-20

```
