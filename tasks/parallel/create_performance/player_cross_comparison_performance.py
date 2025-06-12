from celery import shared_task

from constants.calculation.game.calculation_types import WindowCalculations
from modules.key_creators.ccomparison_key_creator import CrossComparisonPlayerKeyCreator
from modules.key_creators.redis_key_creator import RedisParallelKeyCreator
from modules.query_creators.cross_comparison_query_creator_function import match_ccomparison_query_creator
from tasks.cross_comparison.helpers import COMPARISON_TYPE_POSITION_MAP
from tasks.helpers import get_query_data
from tasks.parallel.decorators import performance_creator_task_decorator
from tasks.task_decorator import processing_task_decorator
from tasks.utils.performance_object_creation.player_cross_comparison_objects import \
    create_player_cross_comparison_performance_objs


@shared_task(name="create_cross_comparison_player_performance", ignore_result=True)
@performance_creator_task_decorator
@processing_task_decorator
def create_cross_comparison_player_performance_task(
        db_session,
        league_id: int | None,
        patch_id: int | None,
        ccomparison_type: int,
        ccomp_pos_id: int,
):
    KEY = RedisParallelKeyCreator(
        processing_type="cross-comparison",
        PoT="player",
        aggregation_type=ccomparison_type,
        league_id=league_id,
        patch_id=patch_id,
        ccomp_pos_id=ccomp_pos_id,
    )
    CCKC = CrossComparisonPlayerKeyCreator(ccomparison_type)

    test_calc_id = next(WindowCalculations.VALUES(only_field="db_id"))

    output = dict()
    enemies = COMPARISON_TYPE_POSITION_MAP[ccomp_pos_id]
    for is_flat in [True, False]:
        query, names = match_ccomparison_query_creator(
            patch_id=patch_id,
            league_id=league_id,
            calculation_type_id=test_calc_id,
            positions=enemies,
            is_flat=is_flat
        )
        data = get_query_data(db_session=db_session, query=query, names=names)

        create_player_cross_comparison_performance_objs(
            league_id=league_id,
            patch_id=patch_id,
            data=data,
            CCKC=CCKC,
            is_flat=is_flat,
            ccomparison_type=ccomparison_type,
            position_type=ccomp_pos_id,
            output=output,
        )

    db_session.commit()

    return output, CCKC, KEY.base
