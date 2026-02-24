from app.satellite_catalog.service import SatelliteCatalogService


def run_update(service: SatelliteCatalogService | None = None) -> None:
    service = service or SatelliteCatalogService()
    service.update_satellite_catalog()
    print("--Satellite catalog update completed--")


if __name__ == "__main__":
    try:
        run_update()
    except Exception as e:
        print(f"--Satellite catalog update failed: {e}--")
        raise
