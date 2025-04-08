from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, add_values
from constants.calculation.game.category import WindowCategories


@add_values
@set_category_and_value(WindowCategories.DEWARD)
class DewardCalculations:
    was_dewarded_sen: CalculationItem = CalculationItem(
        name="was_dewarded_sen",
        description="Number of dewarded sentries",
        index=1,
    )
    was_dewarded_obs: CalculationItem = CalculationItem(
        name="was_dewarded_obs",
        description="Number of dewarded observers",
        index=2,
    )
    was_dewarded_perc_sen: CalculationItem = CalculationItem(
        name="was_dewarded_perc_sen",
        description="Percent of dewarded sentries",
        index=3,
    )
    was_dewarded_perc_obs: CalculationItem = CalculationItem(
        name="was_dewarded_perc_obs",
        description="Percent of dewarded observers",
        index=4,
    )
    killed_sen: CalculationItem = CalculationItem(
        name="killed_sen",
        description="Sentry kills",
        index=5,
    )
    killed_obs: CalculationItem = CalculationItem(
        name="killed_obs",
        description="Observer kills",
        index=6,
    )
    killed_sen_pm: CalculationItem = CalculationItem(
        name="killed_sen_pm",
        description="Sentry kills (per minute)",
        index=7,
    )
    killed_obs_pm: CalculationItem = CalculationItem(
        name="killed_obs_pm",
        description="Observer kills (per minute)",
        index=8,
    )

    VALUES: list[CalculationItem]
    VALUES_NAMES: list[str]
