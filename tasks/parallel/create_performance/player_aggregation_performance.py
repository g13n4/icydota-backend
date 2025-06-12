from celery import shared_task

from modules.key_creators.aggregation_key_creator import AggregationPlayerKeyCreator
from modules.key_creators.redis_key_creator import RedisParallelKeyCreator
from tasks.parallel.decorators import performance_creator_task_decorator
from tasks.task_decorator import processing_task_decorator
from tasks.utils.performance_object_creation.player_aggregation_objects import \
    create_player_aggregation_performance_objs


@shared_task(name="create_aggregate_player_performance", ignore_result=True)
@performance_creator_task_decorator
@processing_task_decorator
def create_aggregate_player_performance_task(
        db_session,
        league_id: int | None,
        patch_id: int | None,
        aggregation_type: int,
) -> tuple[dict, AggregationPlayerKeyCreator, str]:
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
    db_session.commit()

    return output, AGC, KEY.base
