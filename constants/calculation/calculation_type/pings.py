from constants.calculation.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.calculation_type.helpers import CalculationItem, set_category, PostprocessingItem, add_values
from constants.calculation.category import WindowCategories


@add_values
@set_category(WindowCategories.PINGS)
class PingsCalculations:
    pings: CalculationItem = CalculationItem(
        name="pings",
        description="Pings",
        value=42,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    pings_per_minute: CalculationItem = CalculationItem(
        name="pings_per_minute",
        description="Pings (per minute)",
        value=43,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )

    VALUES: list[CalculationItem]
