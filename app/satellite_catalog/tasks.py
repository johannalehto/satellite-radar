import os
from celery import shared_task
from scripts.update_satellite_catalog import run_update

@shared_task(bind=True, retry_backoff=True, max_retries=3)
def scheduled_update(self):
    try:
        run_update()
        return "Scheduled update for satellite catalog completed"
    except Exception as e:
        raise self.retry(exc=e)

