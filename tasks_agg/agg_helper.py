from .approximate_positions import approximate_positions
from .process_aggregation import process_aggregation
from .process_aggregation_cross_comparison import create_cross_comparison_aggregation
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def approximate_positions_helper(league_id: int) -> None:
    approximate_positions.delay(league_id=league_id)


def aggregate_league_helper(league_id: int) -> None:
    process_aggregation.delay(league_id=league_id)


def cross_compare_league_helper(league_id: int) -> None:
    create_cross_comparison_aggregation.delay(league_id)


def post_process_league_id(league_id: int,
                           approx: bool = True,
                           aggregate: bool = True,
                           cross_compare: bool = True) -> None:
    if approx:
        approximate_positions(league_id=league_id)
    if aggregate:
        aggregate_league_helper(league_id=league_id)
    if cross_compare:
        cross_compare_league_helper(league_id=league_id)

