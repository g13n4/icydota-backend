from collections.abc import Iterable
from typing import Any

from constants.performance.total.total import GameTotals
from models import PerformanceTotalData


TOTAL_EXCLUDE_FIELDS = { "id", "performance_id" }


async def to_league_list(leagues: Iterable) -> list[dict[str, str]]:
    data = [(league_id, name, match_id) for league_id, name, match_id in leagues]
    data.sort(key=lambda item: (item[2] is None, item[2], item[0]), reverse=True)

    return [
        {
            "label": name,
            "value": str(league_id),
        } for league_id, name, _ in data
    ]


async def to_basic_list(objs: Iterable) -> list[dict[str, str]]:
    return [
        {
            "label": league.name,
            "value": str(league.id),
        } for league in objs
    ]


async def process_total_output(data: PerformanceTotalData, **kwargs) -> dict:
    """Get Total data"""
    data = data.model_dump(exclude=TOTAL_EXCLUDE_FIELDS)

    for game_total in GameTotals.VALUES:
        if not game_total.field_options.is_required(**kwargs):
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


async def to_field_list(values: Iterable) -> list[dict[str, str | int]]:
    output = []
    for item in values:
        output.append(
            {
                "value": item.name,
                "label": item.description,
            }
        )
    return output
