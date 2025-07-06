from celery import shared_task
from sqlalchemy import update
from sqlmodel import delete, select, Session, col

from db import get_sync_db_session
from models.performance import Performance
from models.performance_data_type import ByTeamType, CrossComparisonType


@shared_task(name="delete_cross_comparison_match", ignore_result=True)
def delete_cross_comparison_match(
        league_id: int | None,
        patch_id: int | None,
        ccomp_type: int | None = None,
        only_mark: bool = True,
):
    db_session: Session = get_sync_db_session(expire=True)
    if patch_id:
        where = [CrossComparisonType.patch_id == patch_id]
    elif league_id:
        where = [CrossComparisonType.league_id == league_id]
    else:
        raise ValueError("No league_id value or patch_id value provided for delete_cross_comparison_match task")

    if ccomp_type:
        where.append(CrossComparisonType.type_id == ccomp_type)

    select_performance_ids = (
        select(Performance.id)
        .join(CrossComparisonType, CrossComparisonType.performance_id == Performance.id)
        .where(
            *where,
            Performance.type_id == Performance.const.game.CROSS_COMPARISON,
        )
    )

    if only_mark:
        db_session.execute(
            update(Performance).where(col(Performance.id).in_(select_performance_ids)).values(outdated=True)
        )
    else:
        db_session.exec(
            delete(Performance).where(col(Performance.id).in_(select_performance_ids))
        )

    db_session.commit()


@shared_task(name="delete_cross_comparison_team", ignore_result=True)
def delete_cross_comparison_team(league_id: int, patch_id: int, only_mark: bool = True):
    db_session: Session = get_sync_db_session(expire=True)
    if patch_id:
        where = [ByTeamType.patch_id == patch_id]
    elif league_id:
        where = [ByTeamType.league_id == league_id]
    else:
        raise ValueError("No league_id value or patch_id value provided for delete_cross_comparison_team task")

    select_performance_ids = (
        select(Performance.id)
        .join(ByTeamType, ByTeamType.performance_id == Performance.id)
        .where(
            *where,
            Performance.type_id == Performance.const.team.TEAM_MATCH_CROSS_COMPARISON,
        )
    )

    if only_mark:
        db_session.execute(
            update(Performance).where(Performance.id.in_(select_performance_ids)).values(outdated=True)
        )
    else:
        db_session.exec(
            delete(Performance).where(Performance.id.in_(select_performance_ids))
        )

    db_session.commit()
