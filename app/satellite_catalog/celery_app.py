import os
from celery import Celery
from app.config import CELERY_BROKER_URL, CELERY_BACKEND_URL


celery = Celery(
    "satellite_catalog",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,
    include=["app.satellite_catalog.tasks"]
)

print(f"Celery is using broker: {CELERY_BROKER_URL}")

celery.conf.update(
    timezone="UTC",
    enable_utc=True
)