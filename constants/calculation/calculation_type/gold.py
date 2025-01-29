from constants.calculation.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.calculation_type.helpers import CalculationItem, set_category, PostprocessingItem, add_values
from constants.calculation.category import WindowCategories


@add_values
@set_category(WindowCategories.GOLD)
class GoldCalculations:
    death_penalty: CalculationItem = CalculationItem(
        name="death_penalty",
        description="Gold removed for death",
        value=104,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    death_penalty_pm: CalculationItem = CalculationItem(
        name="death_penalty_pm",
        description="Gold removed for death (per minute)",
        value=105,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_assist: CalculationItem = CalculationItem(
        name="gold_for_assist",
        description="Gold for assists",
        value=106,
        index=3,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_assist_pm: CalculationItem = CalculationItem(
        name="gold_for_assist_pm",
        description="Gold for assists (per minute)",
        value=107,
        index=4,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_killing_buildings: CalculationItem = CalculationItem(
        name="gold_for_killing_buildings",
        description="Gold for killing buildings",
        value=108,
        index=5,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_killing_buildings_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_buildings_pm",
        description="Gold for killing buildings (per minute)",
        value=109,
        index=6,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_killing_heroes: CalculationItem = CalculationItem(
        name="gold_for_killing_heroes",
        description="Gold for killing heroes",
        value=110,
        index=7,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_killing_heroes_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_heroes_pm",
        description="Gold for killing heroes (per minute)",
        value=111,
        index=8,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_killing_creeps: CalculationItem = CalculationItem(
        name="gold_for_killing_creeps",
        description="Gold for killing creeps",
        value=112,
        index=9,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_killing_creeps_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_creeps_pm",
        description="Gold for killing creeps (per minute)",
        value=113,
        index=10,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_killing_neutrals: CalculationItem = CalculationItem(
        name="gold_for_killing_neutrals",
        description="Gold for killing neutrals",
        value=114,
        index=11,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_killing_neutrals_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_neutrals_pm",
        description="Gold for killing neutrals (per minute)",
        value=115,
        index=12,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_killing_roshan: CalculationItem = CalculationItem(
        name="gold_for_killing_roshan",
        description="Gold for killing roshan",
        value=116,
        index=13,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_killing_roshan_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_roshan_pm",
        description="Gold for killing roshan (per minute)",
        value=117,
        index=14,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_assisting_killing_couriers: CalculationItem = CalculationItem(
        name="gold_for_assisting_killing_couriers",
        description="Gold for courier assists",
        value=118,
        index=15,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_assisting_killing_couriers_pm: CalculationItem = CalculationItem(
        name="gold_for_assisting_killing_couriers_pm",
        description="Gold for courier assists (per minute)",
        value=119,
        index=16,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_runes: CalculationItem = CalculationItem(
        name="gold_runes",
        description="Gold for runes",
        value=120,
        index=17,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_runes_pm: CalculationItem = CalculationItem(
        name="gold_runes_pm",
        description="Gold for runes (per minute)",
        value=121,
        index=18,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_flag_bearer_and_dooms_devour: CalculationItem = CalculationItem(
        name="gold_for_flag_bearer_and_doom's_devour",
        description="Gold for flag bearers, devour, etc",
        value=122,
        index=19,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_flag_bearer_and_dooms_devour_pm: CalculationItem = CalculationItem(
        name="gold_for_flag_bearer_and_doom's_devour_pm",
        description="Gold for flag bearers, devour, etc (per minute)",
        value=123,
        index=20,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_wards: CalculationItem = CalculationItem(
        name="gold_for_wards",
        description="Gold for wards",
        value=124,
        index=21,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_wards_pm: CalculationItem = CalculationItem(
        name="gold_for_wards_pm",
        description="Gold for wards (per minute)",
        value=125,
        index=22,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    gold_for_killing_couriers: CalculationItem = CalculationItem(
        name="gold_for_killing_couriers",
        description="Gold for couriers",
        value=126,
        index=23,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.SUM),
    )
    gold_for_killing_couriers_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_couriers_pm",
        description="Gold for couriers (per minute)",
        value=127,
        index=24,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )

    VALUES: list[CalculationItem]
