from celery import chain
from celery.utils.log import get_task_logger

from constants.aggregation import AggregationConstant
from constants.calculation.cross_comparison import CrossComparisonTypeConstant
from tasks.aggregation.delete import delete_aggregation_match, delete_aggregation_team
from tasks.aggregation.match import aggregate_league_match
from tasks.aggregation.team import aggregate_league_team
from tasks.approximate_positions import approximate_positions
from tasks.cross_comparison.delete import delete_cross_comparison_match, delete_cross_comparison_team
from tasks.cross_comparison.match import cross_comparison_league_match
from tasks.cross_comparison.team import cross_comparison_league_team
from tasks.league.delete import delete_league_task
from tasks.set_comparison_names import set_comparison_names


logger = get_task_logger(__name__)


def approximate_positions_helper(league_id: int) -> None:
    approximate_positions.delay(league_id=league_id)


def delete_league(league_id: int) -> None:
    delete_league_task.si(league_id=league_id)


def aggregate_league_task_helper(league_id: int | None = None, patch_id: int | None = None) -> None:
    aggregation_tasks = chain(
        aggregate_league_match.si(league_id=league_id, patch_id=patch_id, aggregation_type=aggregation_type)
        for aggregation_type in AggregationConstant.VALUES
    )

    all_tasks = (
            delete_aggregation_team.si(league_id=league_id, patch_id=patch_id) |
            aggregate_league_team.si(league_id=league_id, patch_id=patch_id) |
            delete_aggregation_match.si(league_id=league_id, patch_id=patch_id) |
            aggregation_tasks

    )
    all_tasks()


def cross_compare_league_task_helper(league_id: int | None = None, patch_id: int | None = None) -> None:
    ccomparison_tasks = chain(
        cross_comparison_league_match.si(league_id=league_id, patch_id=patch_id, ccomparison_type=ccomparison_type)
        for ccomparison_type in CrossComparisonTypeConstant.VALUES
    )

    all_tasks = (
            delete_cross_comparison_team.si(league_id=league_id, patch_id=patch_id) |
            cross_comparison_league_team.si(league_id=league_id, patch_id=patch_id) |
            delete_cross_comparison_match.si(league_id=league_id, patch_id=patch_id) |
            ccomparison_tasks
    )
    all_tasks()


def set_comparison_names_helper() -> None:
    set_comparison_names.apply_async()
