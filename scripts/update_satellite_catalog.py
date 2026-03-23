from app.satellite_catalog.service import SatelliteCatalogService


def run_update():
    try:
        service = SatelliteCatalogService()
        service.update_satellite_catalog_with_tle_data()
        print("--Satellite catalog updated successfully--")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    run_update()
