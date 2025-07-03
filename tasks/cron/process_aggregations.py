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


@shared_task(name='start_aggregations_and_ccomparison_(cron)')
def start_aggregations_and_ccomparison_cron() -> None:
    db_session: Session = get_sync_db_session()

    logger.info(f"Processing league and patch for aggregation and cross-comparison")

    lop_list = [
        LoPItem(select(League).where(League.should_be_processed == True), "league_id", "league", "leagues"),
        LoPItem(select(Patch).where(Patch.should_be_processed == True), "patch_id", "patch", "patches"),
    ]

    for ntuple in lop_list:

        processed_ids = []
        for obj in db_session.exec(ntuple.query).all():
            kwarg = {
                ntuple.id_name: obj.id
            }

            parallel_aggregate_task_helper(**kwarg)
            parallel_cross_comparison_task_helper(**kwarg)

            obj.should_be_processed = False
            db_session.add(obj)
            processed_ids.append(obj.id)
            logger.info(f"Added {ntuple.singular} to aggregate and cross-compare: {obj.name}")

        logger.info(f"Added {len(processed_ids)} {ntuple.plural} to aggregate and cross-compare")

    db_session.commit()
    db_session.close()
