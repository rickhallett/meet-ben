import os
from functools import lru_cache
from celery import Celery
from config.settings import get_settings

settings = get_settings()

"""
Configuration for Celery.
"""


def get_redis_url():
    """
    Get the Redis URL for Celery configuration.

    Returns:
        str: The Redis URL.
    """
    redis_host = f"{os.getenv('PROJECT_NAME')}_redis"
    return f"redis://{redis_host}:6379/0"


@lru_cache
def get_celery_config():
    """
    Get the Celery configuration.

    Returns:
        dict: The Celery configuration.
    """
    redis_url = get_redis_url()
    return {
        "broker_url": redis_url,
        "result_backend": redis_url,
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "enable_utc": True,
        "broker_connection_retry_on_startup": True,
    }


celery_app = Celery("tasks")
celery_app.config_from_object(get_celery_config())

# Automatically discover and register tasks
celery_app.autodiscover_tasks(["tasks"], force=True)
