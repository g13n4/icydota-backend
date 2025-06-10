from celery import shared_task
import pickle
from redis_app import get_redis_single
from tasks.aggregation.helpers import AggregationKeyCreator
from tasks.aggregation.player.helpers import create_player_aggregation_performance_objs
from tasks.aggregation.player.parallel.helpers import PlayerParallelKeyCreator
from tasks.task_decorator import processing_task_decorator


@shared_task(name="create_aggregate_performance_player", ignore_result=True)
@processing_task_decorator
def create_aggregate_performance_player_task(
        db_session,
        league_id: int | None,
        patch_id: int | None,
        aggregation_type: int,
) -> None:
    r = get_redis_single()
    KEY = PlayerParallelKeyCreator(
        processing_type="aggregation",
        PoT="player",
        aggregation_type=aggregation_type,
        league_id=league_id,
        patch_id=patch_id,
    )
    AGC = AggregationKeyCreator(aggregation_type)

    output = create_player_aggregation_performance_objs(
        db_session=db_session, league_id=league_id, patch_id=patch_id, AGC=AGC,
    )
    db_session.commit()

    data = {
            "performance": {k: v.id for k, v in output.items()},
            "AGC": AGC,
        }
    r.set(KEY.base, pickle.dumps(data))

    return None
