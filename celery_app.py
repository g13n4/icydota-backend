import datetime
import logging
import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, after_setup_task_logger, task_prerun
from dotenv import load_dotenv


load_dotenv()

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

tasks = ['tasks.process_leagues_and_match',
         'tasks.process_game', ]

celery_app = Celery(
    main='icydota',
    enable_utc=True,
    timezone='Europe/Moscow',
    broker=f'redis://default:{REDIS_PASSWORD}@127.0.0.1:6379/0',
    backend=f'redis://default:{REDIS_PASSWORD}@127.0.0.1:6379/0',
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


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Process league games
    sender.add_periodic_task(
        crontab(minute='0', hour='*/6'),
        task='process_league_games_(cron)',
        name='process league games every 6 hours',
    )

    # Update leagues dates
    sender.add_periodic_task(
        crontab(minute='0', hour='12', day_of_week='1,4'),
        task='update_leagues_date_(cron)',
        name='update leagues start and end date every 3-4 days',
    )
