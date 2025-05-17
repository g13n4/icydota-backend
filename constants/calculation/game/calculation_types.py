from constants.calculation.game.calculation_type.damage import DamageCalculations
from constants.calculation.game.calculation_type.deward import DewardCalculations
from constants.calculation.game.calculation_type.gold import GoldCalculations
from constants.calculation.game.calculation_type.helpers import CalculationItem
from constants.calculation.game.calculation_type.interval import IntervalCalculations
from constants.calculation.game.calculation_type.pings import PingsCalculations
from constants.calculation.game.calculation_type.wards import WardsCalculations
from constants.calculation.game.calculation_type.xp import XPCalculations


# class ValuesGetter:
#     VALUES: list[CalculationItem] = (
#             IntervalCalculations.VALUES +
#             PingsCalculations.VALUES +
#             DamageCalculations.VALUES +
#             WardsCalculations.VALUES +
#             DewardCalculations.VALUES +
#             XPCalculations.VALUES +
#             GoldCalculations.VALUES
#     )
#
#
#     def __iter__(self):
#         yield iter(ValuesGetter.VALUES)
#
#     def __call__(self, no_match: bool = False, no_agg: bool = False):
#         for item in self:
#             if no_match and item.no_match:
#                 continue
#             if no_agg and item.no_agg:
#                 continue
#             yield item


class WindowCalculations(
    IntervalCalculations,
    PingsCalculations,
    DamageCalculations,
    WardsCalculations,
    DewardCalculations,
    XPCalculations,
    GoldCalculations
):
    VALUES: list[CalculationItem] = (
            IntervalCalculations.VALUES +
            PingsCalculations.VALUES +
            DamageCalculations.VALUES +
            WardsCalculations.VALUES +
            DewardCalculations.VALUES +
            XPCalculations.VALUES +
            GoldCalculations.VALUES
    )
    VALUES_NAMES: list[str] = (
            IntervalCalculations.VALUES_NAMES +
            PingsCalculations.VALUES_NAMES +
            DamageCalculations.VALUES_NAMES +
            WardsCalculations.VALUES_NAMES +
            DewardCalculations.VALUES_NAMES +
            XPCalculations.VALUES_NAMES +
            GoldCalculations.VALUES_NAMES
    )

    DB_INDEX_MAP: dict[int, int]


WindowCalculations.DB_INDEX_MAP = {
    item.value: item.db_id for item in WindowCalculations.VALUES
}
