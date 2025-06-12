from celery import shared_task

from constants.calculation.game.calculation_types import WindowCalculations
from modules.key_creators import CrossComparisonTeamKeyCreator, RedisParallelKeyCreator
from modules.query_creators.cross_comparison_query_creator_function import (
    team_ccomparison_query_creator,
)
from tasks.helpers import get_query_data
from tasks.parallel.decorators import performance_creator_task_decorator
from tasks.task_decorator import validate_league_and_patch
from tasks.utils.performance_object_creation.team_cross_comparison_objects import \
    create_team_cross_comparison_performance_objs


@shared_task(name="create_cross_comparison_team_performance", ignore_result=True)
@validate_league_and_patch
@performance_creator_task_decorator
def create_cross_comparison_team_performance_task(db_session, league_id: int, patch_id: int | None = None):
    CCTC = CrossComparisonTeamKeyCreator()
    test_calc_id = next(WindowCalculations.VALUES(only_field="db_id"))

    KEY = RedisParallelKeyCreator(
        processing_type="cross-comparison",
        PoT="team",
        aggregation_type=None,
        league_id=league_id,
        patch_id=patch_id,
    )

    output = dict()
    for is_flat in [True, False]:
        query, names = team_ccomparison_query_creator(
            league_id=league_id,
            patch_id=patch_id,
            calculation_type_id=test_calc_id,
            is_flat=is_flat
        )
        data = get_query_data(db_session=db_session, query=query, names=names)

        create_team_cross_comparison_performance_objs(
            db_session=db_session,
            league_id=league_id,
            patch_id=patch_id,
            data=data,
            is_flat=is_flat,
            KC=CCTC,
            output=output,
        )

    return output, KEY.base
