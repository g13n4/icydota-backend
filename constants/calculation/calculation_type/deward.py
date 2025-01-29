from constants.calculation.calculation_type.helpers import CalculationItem, set_category, add_values
from constants.calculation.category import WindowCategories


@add_values
@set_category(WindowCategories.DEWARD)
class DewardCalculations:
    was_dewarded_sen: CalculationItem = CalculationItem(
        name="was_dewarded_sen",
        description="Number of dewarded sentries",
        value=90,
        index=1,
    )
    was_dewarded_obs: CalculationItem = CalculationItem(
        name="was_dewarded_obs",
        description="Number of dewarded observers",
        value=91,
        index=2,
    )
    was_dewarded_perc_sen: CalculationItem = CalculationItem(
        name="was_dewarded_perc_sen",
        description="Percent of dewarded sentries",
        value=92,
        index=3,
    )
    was_dewarded_perc_obs: CalculationItem = CalculationItem(
        name="was_dewarded_perc_obs",
        description="Percent of dewarded observers",
        value=93,
        index=4,
    )
    killed_sen: CalculationItem = CalculationItem(
        name="killed_sen",
        description="Sentry kills",
        value=94,
        index=5,
    )
    killed_obs: CalculationItem = CalculationItem(
        name="killed_obs",
        description="Observer kills",
        value=95,
        index=6,
    )
    killed_sen_pm: CalculationItem = CalculationItem(
        name="killed_sen_pm",
        description="Sentry kills (per minute)",
        value=96,
        index=7,
    )
    killed_obs_pm: CalculationItem = CalculationItem(
        name="killed_obs_pm",
        description="Observer kills (per minute)",
        value=97,
        index=8,
    )

    VALUES: list[CalculationItem]
