from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud.helpers import to_basic_list
from constants.calculation.game.calculation_types import WindowCalculations
from constants.performance.total.total import GameTotals
from models import League, Patch


async def _build_computations() -> list[dict]:
    output = dict()
    for item in WindowCalculations.VALUES:
        category_id = str(item.category.value)
        if category_id not in output:
            output[category_id] = {
                "label": item.category.name,
                "description": item.category.description,
                "value": category_id,
                "items": [],
            }

        output[category_id]["items"].append(
            {
                "label": item.description,
                "value": str(item.db_id),
            }
        )
    return [
        {
            "label": "Total data",
            "value": "0",
        }
    ] + list(output.values())


async def get_initial_data(db: AsyncSession) -> dict:
    patch_objs = await db.exec(select(Patch).where(Patch.aggregation_allowed == True).order_by(Patch.id.desc()))
    league_objs = await db.exec(select(League).order_by(League.id.asc()))
    return {
        "computations": await _build_computations(),
        "totalPercentFields": GameTotals.VALUES(only_pseudo_bools=True, only_field="name"),
        "patch": await to_basic_list(patch_objs),
        "league": await to_basic_list(league_objs),
    }
