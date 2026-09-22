"""
app/tasks/__init__.py
Celery application factory for CommercePulse.

The Celery app is created here and imported by:
  - app/tasks/embed.py  (task definitions)
  - start_worker.bat    (worker process)
  - FastAPI upload routes (to enqueue tasks)
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

REDIS_URL = settings.REDIS_URL

celery_app = Celery(
    "commercepulse",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.services.tasks"],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone
    timezone="Asia/Kolkata",
    enable_utc=True,
    # Reliability
    broker_connection_retry_on_startup=True,
    task_acks_late=True,           # Ack only after task succeeds (safe retry)
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,  # One task at a time (embeddings are CPU-heavy)
    # Result expiry
    result_expires=3600,           # Keep results for 1 hour
    # Beat schedule — nightly re-embed all sellers at 2:00 AM IST
    beat_schedule={
        "nightly-embed-all-sellers": {
            "task": "app.services.tasks.nightly_embed_all",
            "schedule": crontab(hour=2, minute=0),  # 2:00 AM IST daily
        },
        "weekly-ai-health-check": {
            "task": "app.services.tasks.weekly_health_check",
            "schedule": crontab(hour=8, minute=0, day_of_week=1),  # 8:00 AM IST every Monday
        },
    },
)
