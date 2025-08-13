from itertools import product

from celery import chain

from constants.calculation.game.calculation_types import WindowCalculations
from tasks.aggregation.delete import delete_aggregation_team
from tasks.helpers import PROCESSING_COMPARISON_LIST
from tasks.parallel.create_performance.team_aggregation_performance import create_aggregate_team_performance_task
from tasks.parallel.task_helper.helpers import create_partial_task


def team_aggregation_parallel_processor_task_helper(
        league_id: int | None = None,
        patch_id: int | None = None,
):
    ONE_CALC_TASK = create_partial_task("aggregation", "team")
    tasks = []
    # totals
    for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
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
            PROCESSING_COMPARISON_LIST,
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
            delete_aggregation_team.si(league_id=league_id, patch_id=patch_id) |
            create_aggregate_team_performance_task.si(
                league_id=league_id,
                patch_id=patch_id,
            ) | chain(*tasks)
    )
    all_tasks()
