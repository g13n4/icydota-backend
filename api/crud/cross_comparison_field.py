from api.crud.helpers import to_field_list
from constants.performance.total import GameTotals
from constants.performance.window import GameStageWindows, LaneStageWindows


async def get_cross_comparison_fields() -> dict[str, list]:

    return {
        "totals": await to_field_list(GameTotals.VALUES),
        "Lwindows": await to_field_list(LaneStageWindows.VALUES),
        "Gwindows": await to_field_list(GameStageWindows.VALUES),

    }
