from celery import shared_task
from sqlalchemy import update
from sqlmodel import delete, select, Session, col

from db import get_sync_db_session
from models import AggregationType
from models.performance import Performance
from models.performance_data_type import ByTeamType


@shared_task(name="delete_aggregation_match", ignore_result=True)
def delete_aggregation_match(
        league_id: int | None,
        patch_id: int | None,
        aggregation_type: int | None = None,
        only_mark: bool = True,
):
    db_session: Session = get_sync_db_session(expire=False)
    if patch_id:
        where = [AggregationType.patch_id == patch_id]
    elif league_id:
        where = [AggregationType.league_id == league_id]
    else:
        raise ValueError("No league_id value or patch_id value provided for delete_aggregation_match task")

    if aggregation_type:
        where.append(AggregationType.type_id == aggregation_type)

    select_performance_ids = (
        select(Performance.id)
        .join(AggregationType, AggregationType.performance_id == Performance.id)
        .where(
            *where,
            col(Performance.type_id).in_(
                [
                    Performance.const.game.AGGREGATION,
                    Performance.const.game.AGGREGATION_COMPARISON,
                ]
            )
        ))

    if only_mark:
        db_session.execute(
            update(Performance).where(col(Performance.id).in_(select_performance_ids)).values(outdated=True)
        )
    else:
        db_session.exec(
            delete(Performance).where(col(Performance.id).in_(select_performance_ids))
        )

    db_session.commit()


@shared_task(name="delete_aggregation_team", ignore_result=True)
def delete_aggregation_team(league_id: int | None, patch_id: int | None, only_mark: bool = True):
    db_session: Session = get_sync_db_session(expire=False)
    if patch_id:
        where = [ByTeamType.patch_id == patch_id]
    elif league_id:
        where = [ByTeamType.league_id == league_id]
    else:
        raise ValueError("No league_id value or patch_id value provided for delete_aggregation_team task")

    select_performance_ids = (select(Performance.id)
    .join(ByTeamType, ByTeamType.performance_id == Performance.id)
    .where(
        *where,
        col(Performance.type_id).in_(
            [
                Performance.const.team.TEAM_MATCH_AGGREGATION,
                Performance.const.team.TEAM_MATCH_AGGREGATION_COMPARISON,
            ]
        )
    ))

    if only_mark:
        db_session.execute(
            update(Performance).where(col(Performance.id).in_(select_performance_ids)).values(outdated=True)
        )
    else:
        db_session.exec(
            delete(Performance).where(col(Performance.id).in_(select_performance_ids))
        )
    db_session.commit()
