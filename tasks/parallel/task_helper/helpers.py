from functools import partial
from typing import Literal

from tasks.parallel.process_calculation import process_one_calculation_aggregate_player_task


def create_partial_task(processing_type: Literal["aggregation", "cross-comparison"], PoT: Literal["player", "team"]):
    return partial(
        process_one_calculation_aggregate_player_task.si,
        processing_type=processing_type,
        PoT=PoT,
    )
