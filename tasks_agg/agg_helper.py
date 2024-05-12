from .approximate_positions import approximate_positions
from .remove_data import remove_aggregation_data
from .process_aggregation import process_aggregation
from .process_aggregation_cross_comparison import create_cross_comparison_aggregation
from .set_comparison_names import set_comparison_names
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def approximate_positions_helper(league_id: int) -> None:
    approximate_positions.delay(league_id=league_id)


def aggregate_league_helper(league_id: int) -> None:
    (remove_aggregation_data.si(league_id=league_id, cross_comparison=False) |
     process_aggregation.si(league_id=league_id)).apply_async()


def cross_compare_league_helper(league_id: int) -> None:
    (remove_aggregation_data.si(league_id=league_id, cross_comparison=False) |
     create_cross_comparison_aggregation.si(league_id=league_id)).apply_async()


def set_comparison_names_helper() -> None:
    set_comparison_names.apply_async()
