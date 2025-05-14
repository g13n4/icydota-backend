from constants.calculation.game.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, \
    PostprocessingItem, add_values
from constants.calculation.game.category import WindowCategories


@add_values
@set_category_and_value(WindowCategories.WARDS)
class WardsCalculations:
    placed_wards_sen: CalculationItem = CalculationItem(
        name="placed_wards_sen",
        description="Placed sentries",
        index=1,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    placed_wards_obs: CalculationItem = CalculationItem(
        name="placed_wards_obs",
        description="Placed observers",
        index=2,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )

    VALUES: list[CalculationItem]
    VALUES_NAMES: list[str]
