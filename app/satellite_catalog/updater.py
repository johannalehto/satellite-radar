from app.satellite_catalog.service import SatelliteCatalogService


def run_update() -> None:
    service = SatelliteCatalogService()
    service.update_satellite_catalog()
    print("--Satellite catalog update completed--")


if __name__ == "__main__":
    try:
        run_update()
    except Exception as e:
        print(f"--Satellite catalog update failed: {e}--")
        raise
