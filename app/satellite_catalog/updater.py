from app.satellite_catalog.service import SatelliteCatalogService


def run_tle_update(service: SatelliteCatalogService | None = None) -> None:
    service = service or SatelliteCatalogService()
    service.update_satellite_catalog_with_tle_data()
    print("--Satellite TLE update completed--")


# TODO: Might be deprecated
def run_update(service: SatelliteCatalogService | None = None) -> None:
    service = service or SatelliteCatalogService()
    service.update_satellite_catalog()
    print("--Satellite catalog update completed--")


if __name__ == "__main__":
    try:
        run_tle_update()
    except Exception as e:
        print(f"--Satellite TLE update failed: {e}--")
        raise
