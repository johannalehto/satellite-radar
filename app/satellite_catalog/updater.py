from app.satellite_catalog.service import SatelliteCatalogService


def run_catalog_update(service: SatelliteCatalogService | None = None) -> None:
    service = service or SatelliteCatalogService()
    service.update_satellite_catalog_with_tle_data()
    service.update_satellite_catalog_with_metadata()
    print("--Satellite catalog update completed--")


def run_tle_update(service: SatelliteCatalogService | None = None) -> None:
    service = service or SatelliteCatalogService()
    service.update_satellite_catalog_with_tle_data()
    print("--Satellite TLE update completed--")


if __name__ == "__main__":
    try:
        run_catalog_update()
    except Exception as e:
        print(f"--Satellite catalog update failed: {e}--")
        raise
