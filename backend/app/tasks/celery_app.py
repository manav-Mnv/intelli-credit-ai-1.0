from celery import Celery
from app.config import settings

celery_app = Celery(
    "intellicredit",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.analysis_pipeline"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_soft_time_limit=300,  # 5 min
    task_time_limit=600,        # 10 min hard limit
)
