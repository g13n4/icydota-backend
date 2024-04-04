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
