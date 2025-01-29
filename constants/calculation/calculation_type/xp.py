from constants.calculation.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.calculation_type.helpers import CalculationItem, set_category, PostprocessingItem, add_values
from constants.calculation.category import WindowCategories


@add_values
@set_category(WindowCategories.XP)
class XPCalculations:
    other_reason: CalculationItem = CalculationItem(
        name="other_reason",
        description="Other XP",
        value=98,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    xp_for_heroes: CalculationItem = CalculationItem(
        name="xp_for_heroes",
        description="XP for heroes",
        value=99,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    xp_for_heroes_pm: CalculationItem = CalculationItem(
        name="xp_for_heroes_pm",
        description="XP for heroes (per minute)",
        value=100,
        index=3,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    xp_for_creeps: CalculationItem = CalculationItem(
        name="xp_for_creeps",
        description="XP for creeps",
        value=101,
        index=4,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    xp_for_creeps_pm: CalculationItem = CalculationItem(
        name="xp_for_creeps_pm",
        description="XP for creeps (per minute)",
        value=102,
        index=5,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    xp_for_roshan: CalculationItem = CalculationItem(
        name="xp_for_roshan",
        description="XP for roshan",
        value=103,
        index=6,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )

    VALUES: list[CalculationItem]
