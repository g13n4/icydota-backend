from collections import namedtuple

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, text

from db import get_sync_db_session
from tasks.aggregation_tasks_helper import parallel_aggregate_task_helper, parallel_cross_comparison_task_helper


logger = get_task_logger(__name__)

LoPItem = namedtuple(
    'LoPItem', [
        "query",
        'field',
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
            "select distinct l.id from players_game_data pgd JOIN games g ON pgd.game_id = g.id"
            "JOIN leagues l ON g.league_id = l.id WHERE pgd.created_at > l.processed_at GROUP BY l.id",
            "league_id",
            "league",
            "leagues"
        )
    elif process_patch:
        data_tuple = LoPItem(
            "select distinct p.id from players_game_data pgd JOIN games g ON pgd.game_id = g.id"
            "JOIN patches p ON g.patch_id = p.id WHERE pgd.created_at > p.processed_at GROUP BY p.id",
            "patch_id",
            "patch",
            "patches"
        )
    else:
        raise TypeError("No argument provided")

    processed_ids = []
    for obj in db_session.execute(
            text(
                data_tuple.query
            )
    ).all():
        kwarg = { data_tuple.field: obj.id }

        parallel_aggregate_task_helper(**kwarg)
        parallel_cross_comparison_task_helper(**kwarg)

        obj.should_be_processed = False
        db_session.add(obj)
        processed_ids.append(obj.id)
        logger.info(f"Added {data_tuple.singular} to aggregate and cross-compare: {obj.name}")

        logger.info(f"Added {len(processed_ids)} {data_tuple.plural} to aggregate and cross-compare")

    db_session.commit()
    db_session.close()
