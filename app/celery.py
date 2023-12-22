from celery import Celery

celery_app = Celery()


class CeleryConfig:
    main = 'icydota'
    enable_utc = True
    timezone = 'Europe/Moscow'
    broker = 'redis://127.0.0.1:6379/0',
    backend = 'redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup = True


celery_app.config_from_object(CeleryConfig)
