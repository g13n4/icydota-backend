from celery import shared_task

from modules.key_creators import AggregationPlayerKeyCreator, RedisParallelKeyCreator
from tasks.parallel.decorators import performance_creator_task_decorator
from tasks.task_decorator import validate_league_and_patch
from tasks.utils.performance_object_creation.player_aggregation_objects import \
    create_player_aggregation_performance_objs


@shared_task(name="create_aggregate_player_performance", ignore_result=True)
@validate_league_and_patch
@performance_creator_task_decorator
def create_aggregate_player_performance_task(
        db_session,
        league_id: int | None,
        patch_id: int | None,
        aggregation_type: int,
) -> tuple[dict, str]:
    KEY = RedisParallelKeyCreator(
        processing_type="aggregation",
        PoT="player",
        aggregation_type=aggregation_type,
        league_id=league_id,
        patch_id=patch_id,
    )
    AGC = AggregationPlayerKeyCreator(aggregation_type)

    output = create_player_aggregation_performance_objs(
        db_session=db_session, league_id=league_id, patch_id=patch_id, AGC=AGC,
    )


    return output, KEY.base
