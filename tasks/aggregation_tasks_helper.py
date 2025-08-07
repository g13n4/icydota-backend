from celery import chain
from celery.utils.log import get_task_logger

from constants.aggregation import AggregationConstant
from constants.calculation.cross_comparison import CrossComparisonTypeConstant
from tasks.aggregation.delete import delete_aggregation_match, delete_aggregation_team
from tasks.aggregation.player import aggregate_league_player_task
from tasks.aggregation.team import aggregate_league_team_task
from tasks.approximate_positions import approximate_positions
from tasks.cross_comparison.delete import delete_cross_comparison_match, delete_cross_comparison_team
from tasks.cross_comparison.match import cross_compare_player_task
from tasks.cross_comparison.team import cross_compare_team_task
from tasks.parallel.task_helper.player_aggregation_task_helper import player_aggregation_parallel_processor_task_helper
from tasks.parallel.task_helper.player_cross_comparison_task_helper import \
    player_cross_comparison_parallel_processor_task_helper
from tasks.parallel.task_helper.team_aggregation_task_helper import team_aggregation_parallel_processor_task_helper
from tasks.parallel.task_helper.team_cross_comparison_task_helper import \
    team_cross_comparison_parallel_processor_task_helper
from tasks.set_comparison_names import set_comparison_names


logger = get_task_logger(__name__)


def approximate_positions_helper(league_id: int) -> None:
    approximate_positions.delay(league_id=league_id)


def delete_league_task_helper(league_id: int | None = None, patch_id: int | None = None) -> None:
    all_deletion_tasks = (
            delete_aggregation_team.si(league_id=league_id, patch_id=patch_id) |
            delete_aggregation_match.si(league_id=league_id, patch_id=patch_id)
    )
    all_deletion_tasks()


def aggregate_league_task_helper(
        league_id: int | None = None,
        patch_id: int | None = None,
        atype: int | None = None,
) -> None:
    if atype is not None:
        if atype:
            aggregate_league_player_task.si(
                league_id=league_id,
                patch_id=patch_id,
                aggregation_type=atype
            ).apply_async()
        else:
            aggregate_league_team_task.si(league_id=league_id, patch_id=patch_id).apply_async()
    else:
        aggregation_tasks = chain(
            aggregate_league_player_task.si(league_id=league_id, patch_id=patch_id, aggregation_type=aggregation_type)
            for aggregation_type in AggregationConstant.VALUES
        )

        all_tasks = (
                aggregate_league_team_task.si(league_id=league_id, patch_id=patch_id) |
                aggregation_tasks
        )
        all_tasks()


def parallel_aggregate_task_helper(
        league_id: int | None = None,
        patch_id: int | None = None,
) -> None:
    player_aggregation_parallel_processor_task_helper(league_id=league_id, patch_id=patch_id)
    team_aggregation_parallel_processor_task_helper(league_id=league_id, patch_id=patch_id)



def delete_cross_comparison_task_helper(league_id: int | None = None, patch_id: int | None = None) -> None:
    all_deletion_tasks = (
            delete_cross_comparison_team.si(league_id=league_id, patch_id=patch_id) |
            delete_cross_comparison_match.si(league_id=league_id, patch_id=patch_id)
    )
    all_deletion_tasks()


def cross_compare_league_task_helper(league_id: int | None = None, patch_id: int | None = None) -> None:
    ccomparison_tasks = chain(
        cross_compare_player_task.si(league_id=league_id, patch_id=patch_id, ccomparison_type=ccomparison_type)
        for ccomparison_type in CrossComparisonTypeConstant.VALUES
    )

    all_tasks = (
            cross_compare_team_task.si(league_id=league_id, patch_id=patch_id) |
            ccomparison_tasks
    )
    all_tasks()


def parallel_cross_comparison_task_helper(
        league_id: int | None = None,
        patch_id: int | None = None,
) -> None:
    player_cross_comparison_parallel_processor_task_helper(league_id=league_id, patch_id=patch_id)
    team_cross_comparison_parallel_processor_task_helper(league_id=league_id, patch_id=patch_id)


def set_comparison_names_helper() -> None:
    set_comparison_names.apply_async()
