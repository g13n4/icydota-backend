import datetime
import logging
import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, after_setup_task_logger, task_prerun
from dotenv import load_dotenv


load_dotenv()

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_ADDRESS = os.getenv('REDIS_ADDRESS', default="127.0.0.1")

tasks = [
    'tasks.aggregation',
    'tasks.cron',
    'tasks.parallel',
    'tasks.game',
    'tasks.league',
]

celery_app = Celery(
    main='icydota',
    enable_utc=True,
    timezone='Europe/Moscow',
    broker=f'redis://default:{REDIS_PASSWORD}@{REDIS_ADDRESS}:6379/0',
    broker_url=f'redis://default:{REDIS_PASSWORD}@{REDIS_ADDRESS}:6379/0',
    result_backend=f'redis://default:{REDIS_PASSWORD}@{REDIS_ADDRESS}:6379/0',
    celery_broker_url=f'redis://default:{REDIS_PASSWORD}@{REDIS_ADDRESS}:6379/0',
    celery_result_backend=f'redis://default:{REDIS_PASSWORD}@{REDIS_ADDRESS}:6379/0',
    result_expires=60 * 60 * 24,
    celery_result_expires=60 * 60 * 24,
    celery_cache_backend='redis',
    broker_transport='redis',
    broker_connection_retry_on_startup=True,
    worker_hijack_root_logger=False,
    include=tasks,
)

logger = logging.getLogger(__name__)

base_message_format = "%(levelname)s|%(asctime)s|%(processName)s|%(processName)s|%(args)s"


@after_setup_logger.connect
def setup_worker_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(base_message_format + '|> %(message)s')
    current_time = datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')

    fh = logging.FileHandler(f'./logs/workers/worker_{current_time}.log', mode='a')
    fh.setLevel(logging.WARNING)
    fh.setFormatter(formatter)

    logger.addHandler(fh)


@after_setup_task_logger.connect
def setup_task_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(base_message_format + '[%(task_id)s|%(task_name)s]|> %(message)s')
    current_time = datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')

    fh = logging.FileHandler(f'./logs/tasks/task_{current_time}.log', mode='a')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    logger.addHandler(fh)


@task_prerun.connect
def setup_task_post_run(task, *args, **kwargs):
    logger.info(f"{task.name}|{task.request.id}|args: {args}|kwargs: {kwargs['kwargs']}")


def strict_cron_time(task_name: str, time_start: int, time_step: int):
    return {
        f'{task_name}_[at {x}]': {
            'task': task_name,
            'schedule': crontab(minute='0', hour=str(x)),
        } for x in range(time_start, 24, time_step)
    }


celery_app.conf.beat_schedule = {
    # 'update_leagues_date': {
    #     'task': 'update_leagues_date_(cron)',
    #     'schedule': crontab(minute='0', hour='12', day_of_week='1,4'),
    # },
    **strict_cron_time('find_leagues_to_process_(cron)', time_start=0, time_step=6),
    **strict_cron_time('reprocess_mispositioned_league_games_(cron)', time_start=3, time_step=3),
    **strict_cron_time('aggregate_and_ccomp_league_and_patch_(cron)', time_start=6, time_step=12),
    'attempt_to_process_bad_games_[at_18]': {
        'task': 'attempt_to_process_bad_games_(cron)',
        'schedule': crontab(minute='0', hour='18', day_of_week='1,3,5'),
    }
}
