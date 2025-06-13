from itertools import product

from celery import chain

from constants.calculation.cross_comparison import CrossComparisonTypeConstant
from constants.calculation.game.calculation_types import WindowCalculations
from tasks.cross_comparison.delete import delete_cross_comparison_match
from tasks.cross_comparison.helpers import COMPARISON_TYPE_POSITION_MAP
from tasks.helpers import PROCESSING_COMPARISON_LIST
from tasks.parallel.create_performance.player_cross_comparison_performance import \
    create_cross_comparison_player_performance_task
from tasks.parallel.task_helper.helpers import create_partial_task


def player_cross_comparison_parallel_processor_task_helper(
        league_id: int | None = None,
        patch_id: int | None = None,
):
    ONE_CALC_TASK = create_partial_task("cross-comparison", "player")
    for ccomparison_type in CrossComparisonTypeConstant.VALUES:
        for ccomp_pos_id in COMPARISON_TYPE_POSITION_MAP.keys():
            # calculations
            tasks = []
            for calc_id, comp_data in product(
                    WindowCalculations.VALUES(only_field="db_id"),
                    PROCESSING_COMPARISON_LIST[1:],
            ):
                is_comparison, is_flat = comp_data
                tasks.append(
                    ONE_CALC_TASK(
                        league_id=league_id,
                        patch_id=patch_id,
                        calculation_id=calc_id,
                        ccomparison_type=ccomparison_type,
                        ccomp_pos_id=ccomp_pos_id,
                        is_comparison=is_comparison,
                        is_flat=is_flat,
                    )
                )
            # totals
            for is_comparison, is_flat in PROCESSING_COMPARISON_LIST[1:]:
                tasks.append(
                    ONE_CALC_TASK(
                        league_id=league_id,
                        patch_id=patch_id,
                        ccomparison_type=ccomparison_type,
                        ccomp_pos_id=ccomp_pos_id,
                        calculation_id=0,
                        is_comparison=is_comparison,
                        is_flat=is_flat,
                    )
                )
            # tasks creation
            all_tasks = (
                    delete_cross_comparison_match.si(league_id=league_id, patch_id=patch_id) |
                    create_cross_comparison_player_performance_task.si(
                        league_id=league_id,
                        patch_id=patch_id,
                        ccomparison_type=ccomparison_type,
                        ccomp_pos_id=ccomp_pos_id,
                    ) | chain(*tasks)
            )
            all_tasks()
