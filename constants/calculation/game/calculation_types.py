from constants.calculation.game.calculation_type.damage import DamageCalculations
from constants.calculation.game.calculation_type.deward import DewardCalculations
from constants.calculation.game.calculation_type.gold import GoldCalculations
from constants.calculation.game.calculation_type.helpers import add_values, CalculationItem
from constants.calculation.game.calculation_type.interval import IntervalCalculations
from constants.calculation.game.calculation_type.pings import PingsCalculations
from constants.calculation.game.calculation_type.wards import WardsCalculations
from constants.calculation.game.calculation_type.xp import XPCalculations


@add_values
class WindowCalculations(
    IntervalCalculations,
    PingsCalculations,
    DamageCalculations,
    WardsCalculations,
    DewardCalculations,
    XPCalculations,
    GoldCalculations
):
    VALUES: list[CalculationItem]
