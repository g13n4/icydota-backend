from celery import shared_task
from sqlmodel import delete, select, Session

from db import get_sync_db_session
from models import AggregationType
from models.performance import Performance
from models.performance_data_type import ByTeamType


@shared_task(name="delete_aggregation_league_match", ignore_result=True)
def delete_aggregation_league_match(league_id: int):
    db_session: Session = get_sync_db_session(expire=False)

    select_performance_ids = (select(Performance.id)
    .join(AggregationType, AggregationType.performance_id == Performance.id)
    .where(
        AggregationType.league_id == league_id,
        Performance.type_id.in_(
            Performance.const.game.AGGREGATION,
            Performance.const.game.AGGREGATION_COMPARISON,
        )
    ))

    db_session.exec(
        delete(Performance).where(Performance.id.in_(select_performance_ids))
    )
    db_session.commit()


@shared_task(name="delete_aggregation_league_team", ignore_result=True)
def delete_aggregation_league_team(league_id: int):
    db_session: Session = get_sync_db_session(expire=False)

    select_performance_ids = (select(Performance.id)
    .join(ByTeamType, ByTeamType.performance_id == Performance.id)
    .where(
        ByTeamType.league_id == league_id,
        Performance.type_id.in_(
            Performance.const.team.TEAM_MATCH_AGGREGATION,
            Performance.const.team.TEAM_MATCH_AGGREGATION_COMPARISON,
        )
    ))

    db_session.exec(
        delete(Performance).where(Performance.id.in_(select_performance_ids))
    )
    db_session.commit()
