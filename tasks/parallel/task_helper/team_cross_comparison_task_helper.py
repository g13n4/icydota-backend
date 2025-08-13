from itertools import product

from celery import chain

from constants.calculation.game.calculation_types import WindowCalculations
from tasks.cross_comparison.delete import delete_cross_comparison_team
from tasks.helpers import PROCESSING_COMPARISON_LIST
from tasks.parallel.create_performance.team_cross_comparison_performance import \
    create_cross_comparison_team_performance_task
from tasks.parallel.task_helper.helpers import create_partial_task


def team_cross_comparison_parallel_processor_task_helper(
        league_id: int | None = None,
        patch_id: int | None = None,
):
    ONE_CALC_TASK = create_partial_task("cross-comparison", "team")
    tasks = []
    # totals
    for is_comparison, is_flat in PROCESSING_COMPARISON_LIST[1:]:
        tasks.append(
            ONE_CALC_TASK(
                league_id=league_id,
                patch_id=patch_id,
                calculation_id=None,
                is_comparison=is_comparison,
                is_flat=is_flat,
            )
        )
    # calculations
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
                is_comparison=is_comparison,
                is_flat=is_flat,
            )
        )
    # tasks creation
    all_tasks = (
            delete_cross_comparison_team.si(league_id=league_id, patch_id=patch_id) |
            create_cross_comparison_team_performance_task.si(
                league_id=league_id,
                patch_id=patch_id,
            ) | chain(*tasks)
    )
    all_tasks()
