from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, add_values
from constants.calculation.game.category import WindowCategories


@add_values
@set_category_and_value(WindowCategories.BUYBACK)
class BuybackCalculations:
    potential_gold_loss: CalculationItem = CalculationItem(
        name="potential_gold_loss",
        description="Gold loss due to death",
        index=1,
    )
    potential_xp_loss: CalculationItem = CalculationItem(
        name="potential_xp_loss",
        description="XP loss due to death",
        index=2,
    )
    has_buyback_time: CalculationItem = CalculationItem(
        name="has_buyback_time",
        description="Time with buyback available",
        index=3,
    )
    has_buyback_percent: CalculationItem = CalculationItem(
        name="has_buyback_percent",
        description="Share of time with buyback available",
        index=4,
    )
    has_no_buyback_time: CalculationItem = CalculationItem(
        name="has_no_buyback_time",
        description="Time with no buyback available",
        index=5,
    )
    has_no_buyback_percent: CalculationItem = CalculationItem(
        name="has_no_buyback_percent",
        description="Share of time with no buyback available",
        index=6,
    )

    VALUES: list[CalculationItem]
    VALUES_NAMES: list[str]
