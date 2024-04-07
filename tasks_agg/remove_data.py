from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select, col

from db import get_sync_db_session
from models import DataAggregationType, GamePerformance


logger = get_task_logger(__name__)


@shared_task(name="remove_aggregation_data", ignore_result=True)
def remove_aggregation_data(league_id: int, cross_comparison: bool) -> None:
    logger.info(f'Removing data for league {league_id}...')

    db_session: Session = get_sync_db_session()

    aggregated_games_obj = db_session.exec(select(DataAggregationType)
                                           .join(GamePerformance)
                                           .where(DataAggregationType.league_id == league_id,
                                                  GamePerformance.is_aggregation == True,
                                                  GamePerformance.cross_comparison == cross_comparison)).all()
    # deleting old aggregations
    if aggregated_games_obj:
        games_performance_objs = db_session.exec(select(GamePerformance)
                                                 .where(col(GamePerformance.aggregation_id)
                                                        .in_([x.id for x in aggregated_games_obj]))).all()
        for obj in games_performance_objs:
            db_session.delete(obj)
        db_session.commit()
    else:
        logger.info(f'No data for league {league_id} found')
