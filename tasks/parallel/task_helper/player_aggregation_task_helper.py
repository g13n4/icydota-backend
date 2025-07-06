from itertools import product

from celery import chain

from constants.aggregation import AggregationConstant
from constants.calculation.game.calculation_types import WindowCalculations
from tasks.aggregation.delete import delete_aggregation_match
from tasks.helpers import PROCESSING_COMPARISON_LIST
from tasks.parallel.create_performance.player_aggregation_performance import create_aggregate_player_performance_task
from tasks.parallel.task_helper.helpers import create_partial_task


def player_aggregation_parallel_processor_task_helper(
        league_id: int | None = None,
        patch_id: int | None = None,
):
    ONE_CALC_TASK = create_partial_task("aggregation", "player")
    for agg_type in AggregationConstant.VALUES:
        tasks = []
        # totals
        for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
            tasks.append(
                ONE_CALC_TASK(
                    league_id=league_id,
                    patch_id=patch_id,
                    aggregation_type=agg_type,
                    calculation_id=0,
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
                    aggregation_type=agg_type,
                    is_comparison=is_comparison,
                    is_flat=is_flat,
                )
            )
        # tasks creation
        all_tasks = (
                delete_aggregation_match.si(league_id=league_id, patch_id=patch_id, aggregation_type=agg_type) |
                create_aggregate_player_performance_task.si(
                    league_id=league_id,
                    patch_id=patch_id,
                    aggregation_type=agg_type,
                ) | chain(*tasks)
        )
        all_tasks()
