from app.satellite_catalog.celestrak_service import CelestrakService


def run_calculate_positions():
    service = CelestrakService()
    service.calculate_positions()
    print("Ran calculate_positions")


if __name__ == "__main__":
    run_calculate_positions()
