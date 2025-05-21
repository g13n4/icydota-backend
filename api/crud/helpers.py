from collections.abc import Iterable
from typing import Any

from constants.performance.total import FieldAvailability, GameTotals
from models import PerformanceTotalData

TOTAL_EXCLUDE_FIELDS = { "id", "performance_id" }

async def to_basic_list(objs: Iterable) -> list[dict]:
    return [
        {
            "label": league.name,
            "value": league.id,
        } for league in objs
    ]


async def process_total_output(data: PerformanceTotalData,
                               *,
                               match: bool = False,
                               aggregation: bool = False,
                               cross_comparison: bool = False) -> dict:
    """Get Total data"""
    data = data.model_dump(exclude=TOTAL_EXCLUDE_FIELDS)

    for game_total in GameTotals.VALUES:
        if not game_total.availability.required(match, aggregation, cross_comparison):
            del data[game_total.name]
            continue

        value = data[game_total.name]
        if game_total.pseudo_bool and value is not None:
            data[game_total.name] = value * 100

    return data



def to_front_bool(value: Any) -> str:
    if value:
        return "Yes"
    return "No"
