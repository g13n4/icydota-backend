import datetime

from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud.helpers import to_basic_list, to_league_list
from constants.calculation.game.calculation_types import WindowCalculations
from constants.performance.total.total import GameTotals
from models import Patch


CACHE = dict()


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
    key = datetime.datetime.now().hour
    if key not in CACHE:
        patch_objs = await db.exec(select(Patch).where(Patch.aggregation_allowed == True).order_by(Patch.id.desc()))
        league_data = await db.execute(
            text(
                """
                        select distinct leagues.id, leagues.name, MAX(games.id) 
                        from leagues
                        LEFT JOIN games ON games.league_id = leagues.id
                        GROUP by leagues.id
                        ORDER BY MAX(games.id)
                        """
            )
        )

        data = {
            "computations": await _build_computations(),
            "patch": await to_basic_list(patch_objs),
            "league": await to_league_list(league_data),
            "totalPercentFields": list(GameTotals.VALUES(only_pseudo_bools=True, only_field="name")),
        }

        CACHE.clear()
        CACHE[key] = data
    else:
        data = CACHE[key]

    return data
