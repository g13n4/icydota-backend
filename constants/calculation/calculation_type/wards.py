from constants.calculation.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.calculation_type.helpers import CalculationItem, set_category, PostprocessingItem, add_values
from constants.calculation.category import WindowCategories


@add_values
@set_category(WindowCategories.WARDS)
class WardsCalculations:
    placed_wards_sen: CalculationItem = CalculationItem(
        name="placed_wards_sen",
        description="Placed sentries",
        value=88,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    placed_wards_obs: CalculationItem = CalculationItem(
        name="placed_wards_obs",
        description="Placed observers",
        value=89,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )

    VALUES: list[CalculationItem]
