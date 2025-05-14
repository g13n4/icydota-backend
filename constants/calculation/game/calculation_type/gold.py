from constants.calculation.game.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, \
    PostprocessingItem, add_values
from constants.calculation.game.category import WindowCategories


@add_values
@set_category_and_value(WindowCategories.GOLD)
class GoldCalculations:
    death_penalty: CalculationItem = CalculationItem(
        name="death_penalty",
        description="Gold removed for death",
        index=1,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    death_penalty_pm: CalculationItem = CalculationItem(
        name="death_penalty_pm",
        description="Gold removed for death (per minute)",
        index=2,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_assist: CalculationItem = CalculationItem(
        name="gold_for_assist",
        description="Gold for assists",
        index=3,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_assist_pm: CalculationItem = CalculationItem(
        name="gold_for_assist_pm",
        description="Gold for assists (per minute)",
        index=4,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_killing_buildings: CalculationItem = CalculationItem(
        name="gold_for_killing_buildings",
        description="Gold for killing buildings",
        index=5,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_killing_buildings_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_buildings_pm",
        description="Gold for killing buildings (per minute)",
        index=6,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_killing_heroes: CalculationItem = CalculationItem(
        name="gold_for_killing_heroes",
        description="Gold for killing heroes",
        index=7,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_killing_heroes_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_heroes_pm",
        description="Gold for killing heroes (per minute)",
        index=8,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_killing_creeps: CalculationItem = CalculationItem(
        name="gold_for_killing_creeps",
        description="Gold for killing creeps",
        index=9,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_killing_creeps_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_creeps_pm",
        description="Gold for killing creeps (per minute)",
        index=10,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_killing_neutrals: CalculationItem = CalculationItem(
        name="gold_for_killing_neutrals",
        description="Gold for killing neutrals",
        index=11,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_killing_neutrals_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_neutrals_pm",
        description="Gold for killing neutrals (per minute)",
        index=12,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_killing_roshan: CalculationItem = CalculationItem(
        name="gold_for_killing_roshan",
        description="Gold for killing roshan",
        index=13,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_killing_roshan_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_roshan_pm",
        description="Gold for killing roshan (per minute)",
        index=14,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_assisting_killing_couriers: CalculationItem = CalculationItem(
        name="gold_for_assisting_killing_couriers",
        description="Gold for courier assists",
        index=15,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_assisting_killing_couriers_pm: CalculationItem = CalculationItem(
        name="gold_for_assisting_killing_couriers_pm",
        description="Gold for courier assists (per minute)",
        index=16,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_runes: CalculationItem = CalculationItem(
        name="gold_runes",
        description="Gold for runes",
        index=17,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_runes_pm: CalculationItem = CalculationItem(
        name="gold_runes_pm",
        description="Gold for runes (per minute)",
        index=18,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_flag_bearer_and_dooms_devour: CalculationItem = CalculationItem(
        name="gold_for_flag_bearer_and_doom's_devour",
        description="Gold for flag bearers, devour, etc",
        index=19,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_flag_bearer_and_dooms_devour_pm: CalculationItem = CalculationItem(
        name="gold_for_flag_bearer_and_doom's_devour_pm",
        description="Gold for flag bearers, devour, etc (per minute)",
        index=20,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_wards: CalculationItem = CalculationItem(
        name="gold_for_wards",
        description="Gold for wards",
        index=21,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_wards_pm: CalculationItem = CalculationItem(
        name="gold_for_wards_pm",
        description="Gold for wards (per minute)",
        index=22,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )
    gold_for_killing_couriers: CalculationItem = CalculationItem(
        name="gold_for_killing_couriers",
        description="Gold for couriers",
        index=23,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
            ),
    )
    gold_for_killing_couriers_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_couriers_pm",
        description="Gold for couriers (per minute)",
        index=24,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
            ),
    )

    VALUES: list[CalculationItem]
    VALUES_NAMES: list[str]
