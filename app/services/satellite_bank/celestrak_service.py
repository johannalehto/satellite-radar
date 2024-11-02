from skyfield.api import Topos, load

class CelestrakService:
    def __init__(self):
        self.stations_url = "https://celestrak.com/NORAD/elements/stations.txt"
        self.satellites = load.tle_file(self.stations_url)
        self.ts = load.timescale()
        self.t = self.ts.now()

# # Load TLE data for satellites
#     def load_tle_data(self):
#         satellites = load.tle_file(self.stations_url)
#         return satellites

    lat = 60.1699
    long = 24.9384

    def get_satellite_position(self, lat, long):
        location = Topos(lat, long)
        for satellite in self.satellites:
            difference = satellite - location
            topocentric = difference.at(self.t)
            alt, az, distance = topocentric.altaz()
            print(f"Satellite: {satellite.name}")
            print(f"Altitude: {alt.degrees}, Azimuth: {az.degrees}, Distance: {distance.km} km")



#