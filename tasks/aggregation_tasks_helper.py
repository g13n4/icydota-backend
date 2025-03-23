from celery.utils.log import get_task_logger

from tasks.aggregation.delete import delete_aggregation_league_match, delete_aggregation_league_team
from tasks.aggregation.match import aggregate_league_match
from tasks.aggregation.team import aggregate_league_team
from tasks.cross_comparison.match import cross_comparison_league_match
from tasks.cross_comparison.team import cross_comparison_league_team
from tasks.approximate_positions import approximate_positions
from tasks.cross_comparison.delete import delete_cross_comparison_match, delete_cross_comparison_team
from tasks.league.delete import delete_league_task
from tasks.set_comparison_names import set_comparison_names


logger = get_task_logger(__name__)


def approximate_positions_helper(league_id: int) -> None:
    approximate_positions.delay(league_id=league_id)


def delete_league(league_id: int) -> None:
    delete_league_task.si(league_id=league_id)


def aggregate_league_match_helper(league_id: int) -> None:
    (delete_aggregation_league_match.si(league_id=league_id, cross_comparison=False) |
     aggregate_league_match.si(league_id=league_id)).apply_async()


def aggregate_league_team_helper(league_id: int) -> None:
    (delete_aggregation_league_team.si(league_id=league_id, cross_comparison=False) |
     aggregate_league_team.si(league_id=league_id)).apply_async()


def cross_compare_league_match_helper(league_id: int) -> None:
    (delete_cross_comparison_match.si(league_id=league_id, cross_comparison=True) |
     cross_comparison_league_match.si(league_id=league_id)).apply_async()


def cross_compare_league_team_helper(league_id: int) -> None:
    (delete_cross_comparison_team.si(league_id=league_id, cross_comparison=True) |
     cross_comparison_league_team.si(league_id=league_id)).apply_async()


def set_comparison_names_helper() -> None:
    set_comparison_names.apply_async()
