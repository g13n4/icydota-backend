from celery import shared_task
from sqlmodel import Session

from modules.key_creators import AggregationTeamKeyCreator, RedisParallelKeyCreator
from tasks.parallel.decorators import performance_creator_task_decorator
from tasks.task_decorator import validate_league_and_patch
from tasks.utils.performance_object_creation.team_aggregation_objects import create_team_aggregation_performance_objs


@shared_task(name="create_aggregate_team_performance", ignore_result=True)
@validate_league_and_patch
@performance_creator_task_decorator
def create_aggregate_team_performance_task(
        db_session: Session,
        league_id: int | None,
        patch_id: int | None,
) -> tuple[dict, str]:
    KEY = RedisParallelKeyCreator(
        processing_type="aggregation",
        PoT="team",
        league_id=league_id,
        patch_id=patch_id,
    )
    ATC = AggregationTeamKeyCreator()

    output = create_team_aggregation_performance_objs(
        db_session=db_session,
        league_id=league_id,
        patch_id=patch_id,
        KC=ATC,
    )

    return output, KEY.base
