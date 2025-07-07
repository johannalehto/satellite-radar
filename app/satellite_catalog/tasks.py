from celery import shared_task

from app.satellite_catalog.service import SatelliteCatalogService


@shared_task(bind=True, retry_backoff=True, max_retries=3)
def scheduled_update(self):
    try:
        service = SatelliteCatalogService()
        service.update_satellite_catalog()
        print("--Scheduled update for satellite catalog completed--")
    except Exception as e:
        raise self.retry(exc=e)
