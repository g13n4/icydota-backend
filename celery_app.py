import os

from celery import Celery
from dotenv import load_dotenv


load_dotenv()

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

celery_app = Celery(
    main='icydota',
    enable_utc=True,
    timezone='Europe/Moscow',
    broker=f'redis://default:{REDIS_PASSWORD}@127.0.0.1:6379/0',
    backend=f'redis://default:{REDIS_PASSWORD}@127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True,
)

