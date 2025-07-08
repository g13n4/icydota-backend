from collections import namedtuple

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import League, Patch
from tasks.aggregation_tasks_helper import parallel_aggregate_task_helper, parallel_cross_comparison_task_helper


logger = get_task_logger(__name__)

LoPItem = namedtuple(
    'LoPItem', [
        'query',
        'id_name',
        "singular",
        "plural",
    ]
)


@shared_task(name='aggregate_and_ccomp_league_and_patch_(cron)', ignore_result=True)
def aggregate_and_ccomp_league_and_patch_cron(
        process_league: bool = False,
        process_patch: bool = False,
) -> None:
    db_session: Session = get_sync_db_session(expire=True)

    logger.info(f"Processing league and patch for aggregation and cross-comparison")

    if process_league:
        data_tuple = LoPItem(
            select(League).where(League.should_be_processed == True),
            "league_id",
            "league",
            "leagues"
            )
    elif process_patch:
        data_tuple = LoPItem(select(Patch).where(Patch.should_be_processed == True), "patch_id", "patch", "patches"),
    else:
        raise TypeError("No argument provided")

    processed_ids = []
    for obj in db_session.exec(data_tuple.query).all():
        kwarg = {
            data_tuple.id_name: obj.id
        }

        parallel_aggregate_task_helper(**kwarg)
        parallel_cross_comparison_task_helper(**kwarg)

        obj.should_be_processed = False
        db_session.add(obj)
        processed_ids.append(obj.id)
        logger.info(f"Added {data_tuple.singular} to aggregate and cross-compare: {obj.name}")

        logger.info(f"Added {len(processed_ids)} {data_tuple.plural} to aggregate and cross-compare")

    db_session.commit()
    db_session.close()
