from constants.calculation.game.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, PostprocessingItem, add_values
from constants.calculation.game.category import WindowCategories


@add_values
@set_category_and_value(WindowCategories.XP)
class XPCalculations:
    other_reason: CalculationItem = CalculationItem(
        name="other_reason",
        description="Other XP",
                index=1,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    xp_for_heroes: CalculationItem = CalculationItem(
        name="xp_for_heroes",
        description="XP for heroes",
                index=2,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    xp_for_heroes_pm: CalculationItem = CalculationItem(
        name="xp_for_heroes_pm",
        description="XP for heroes (per minute)",
                index=3,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    xp_for_creeps: CalculationItem = CalculationItem(
        name="xp_for_creeps",
        description="XP for creeps",
                index=4,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    xp_for_creeps_pm: CalculationItem = CalculationItem(
        name="xp_for_creeps_pm",
        description="XP for creeps (per minute)",
                index=5,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    xp_for_roshan: CalculationItem = CalculationItem(
        name="xp_for_roshan",
        description="XP for roshan",
                index=6,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )

    VALUES: list[CalculationItem]
