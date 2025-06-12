from celery import shared_task
from sqlmodel import Session

from constants.calculation.game.calculation_types import WindowCalculations
from modules.key_creators import RedisParallelKeyCreator, CrossComparisonPlayerKeyCreator
from modules.query_creators.cross_comparison_query_creator_function import match_ccomparison_query_creator
from tasks.cross_comparison.helpers import COMPARISON_TYPE_POSITION_MAP
from tasks.helpers import get_query_data
from tasks.parallel.decorators import performance_creator_task_decorator
from tasks.task_decorator import validate_league_and_patch
from tasks.utils.performance_object_creation.player_cross_comparison_objects import \
    create_player_cross_comparison_performance_objs


@shared_task(name="create_cross_comparison_player_performance", ignore_result=True)
@validate_league_and_patch
@performance_creator_task_decorator
def create_cross_comparison_player_performance_task(
        db_session: Session,
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

    first_calc_id = next(WindowCalculations.VALUES(only_field="db_id"))

    output = dict()
    enemies = COMPARISON_TYPE_POSITION_MAP[ccomp_pos_id]
    for is_flat in [True, False]:
        query, names = match_ccomparison_query_creator(
            patch_id=patch_id,
            league_id=league_id,
            calculation_type_id=first_calc_id,
            positions=enemies,
            is_flat=is_flat
        )
        data = get_query_data(db_session=db_session, query=query, names=names)

        create_player_cross_comparison_performance_objs(
            db_session=db_session,
            league_id=league_id,
            patch_id=patch_id,
            data=data,
            CCKC=CCKC,
            is_flat=is_flat,
            ccomparison_type=ccomparison_type,
            position_type=ccomp_pos_id,
            output=output,
        )

    return output, KEY.base
