from constants.calculation.game.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, \
    PostprocessingItem, add_values
from constants.calculation.game.category import WindowCategories


@add_values
@set_category_and_value(WindowCategories.PINGS)
class PingsCalculations:
    pings: CalculationItem = CalculationItem(
        name="pings",
        description="Pings",
        index=1,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
        ),
    )
    pings_per_minute: CalculationItem = CalculationItem(
        name="pings_per_minute",
        description="Pings (per minute)",
        index=2,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
    )

    VALUES: list[CalculationItem]
    VALUES_NAMES: list[str]
