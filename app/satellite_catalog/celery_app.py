import os
from celery import Celery
from app.config import MONGO_URI, CELERY_BROKER_URL, CELERY_BACKEND_URL

os.environ["MONGO_URI"] = MONGO_URI

celery = Celery(
    "satellite_catalog",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,
    include=["app.satellite_catalog.tasks"]
)

celery.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
            "update-satellite-catalog": {
                "task": "app.satellite_catalog.tasks.scheduled_update",
                "schedule": 86400.0,  # every 24 hours
            }
    }
)