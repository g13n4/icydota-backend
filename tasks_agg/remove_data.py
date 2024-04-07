from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select, col, text
from typing import Any

from db import get_sync_db_session
from models import DataAggregationType, GamePerformance


logger = get_task_logger(__name__)


def _to_sql_format(value: Any) -> str:
    if value:
        return 'true'
    return 'false'


def _set_null_values_gp_sql(db_session, values: str) -> None:
    gp = f"""
    UPDATE games_performance
    SET aggregation_id = null, comparison_id = null, player_game_data_id = null
    WHERE id in {values}
    """
    db_session.execute(text(gp))


def _delete_performance_data(db_session, values: str) -> None:
    totals = f"""
        DELETE FROM performance_totals_data
        WHERE game_performance_id in {values}
        """
    db_session.execute(text(totals))

    windows = f"""
        DELETE FROM performance_windows_data
        WHERE game_performance_id in {values}
        """
    db_session.execute(text(windows))


@shared_task(name="remove_aggregation_data", ignore_result=True)
def remove_aggregation_data(league_id: int, cross_comparison: bool) -> None:
    logger.info(f'Removing data for league {league_id}...')

    db_session: Session = get_sync_db_session(expire=False)
    gp_ids = db_session.exec(select(GamePerformance.id)
                             .join(DataAggregationType,
                                   onclause=GamePerformance.aggregation_id == DataAggregationType.id)
                             .where(DataAggregationType.league_id == league_id,
                                    GamePerformance.is_aggregation == True,
                                    GamePerformance.cross_comparison == cross_comparison)).all()

    if gp_ids:
        gp_ids_sql = str(tuple(gp_ids))
        # set fk to null in gp
        logger.info(f'Nullifying fk in Game Performance...')
        _set_null_values_gp_sql(db_session, gp_ids_sql)
        # set fk to null in performance
        logger.info(f'Deleting Performance Data...')
        _delete_performance_data(db_session, gp_ids_sql)
        # delete

        # DON'T DELETE THE GAME PERFORMANCE MODEL HERE BECAUSE IT'S TOO LONG
        # logger.info(f'Deleting Game Performance...')
        # db_session.execute(
        #     text(f"""DELETE FROM games_performance WHERE id IN {gp_ids_sql}""")
        # )

        db_session.commit()
    else:
        logger.info(f'Nothing to delete...')
