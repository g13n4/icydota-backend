from enum import IntEnum

from constants.calculation.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.calculation_type.helpers import CalculationItem, set_category, PostprocessingItem
from constants.calculation.category import WindowCategories


class IntervalCalculationCategory(IntEnum):
    to_all = 1
    from_all = 2

    to_heroes = 3
    from_heroes = 4

    to_creatures = 5
    from_creatures = 6

    to_illusions = 7
    from_illusions = 8

    to_buildings = 9
    from_buildings = 10

    with_summons = 11


class IntervalCalculationMethod(IntEnum):
    mean = 1
    sum = 2
    median = 3
    dmg_inst = 4


@set_category(WindowCategories.DAMAGE)
class DamageCalculations:
    with_summons__sum: CalculationItem = CalculationItem(
        name="with_summons__sum",
        description="With summons (total)",
        value=44,
        index=1,
        processing=(IntervalCalculationCategory.with_summons, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    with_summons__mean: CalculationItem = CalculationItem(
        name="with_summons__mean",
        description="With summons (mean)",
        value=45,
        index=2,
        processing=(IntervalCalculationCategory.with_summons, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    with_summons__median: CalculationItem = CalculationItem(
        name="with_summons__median",
        description="With summons (median)",
        value=46,
        index=3,
        processing=(IntervalCalculationCategory.with_summons, IntervalCalculationMethod.median),

        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    with_summons__dmg_inst: CalculationItem = CalculationItem(
        name="with_summons__dmg_inst",
        description="With summons (number of instances)",
        value=47,
        index=4,
        processing=(IntervalCalculationCategory.with_summons, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_heroes__sum: CalculationItem = CalculationItem(
        name="to_heroes__sum",
        description="To heroes (total)",
        value=48,
        index=5,
        processing=(IntervalCalculationCategory.to_heroes, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_heroes__mean: CalculationItem = CalculationItem(
        name="to_heroes__mean",
        description="To heroes (mean)",
        value=49,
        index=6,
        processing=(IntervalCalculationCategory.to_heroes, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    to_heroes__median: CalculationItem = CalculationItem(
        name="to_heroes__median",
        description="To heroes (median)",
        value=50,
        index=7,
        processing=(IntervalCalculationCategory.to_heroes, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    to_heroes__dmg_inst: CalculationItem = CalculationItem(
        name="to_heroes__dmg_inst",
        description="To heroes (number of instances)",
        value=51,
        index=8,
        processing=(IntervalCalculationCategory.to_heroes, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_buildings__sum: CalculationItem = CalculationItem(
        name="to_buildings__sum",
        description="To buildings (total)",
        value=52,
        index=9,
        processing=(IntervalCalculationCategory.to_buildings, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_buildings__mean: CalculationItem = CalculationItem(
        name="to_buildings__mean",
        description="To buildings (mean)",
        value=53,
        index=10,
        processing=(IntervalCalculationCategory.to_buildings, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    to_buildings__median: CalculationItem = CalculationItem(
        name="to_buildings__median",
        description="To buildings (median)",
        value=54,
        index=11,
        processing=(IntervalCalculationCategory.to_buildings, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    to_buildings__dmg_inst: CalculationItem = CalculationItem(
        name="to_buildings__dmg_inst",
        description="To buildings (number of instances)",
        value=55,
        index=12,
        processing=(IntervalCalculationCategory.to_buildings, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_creatures__sum: CalculationItem = CalculationItem(
        name="to_creatures__sum",
        description="To npcs (total)",
        value=56,
        index=13,
        processing=(IntervalCalculationCategory.to_creatures, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_creatures__mean: CalculationItem = CalculationItem(
        name="to_creatures__mean",
        description="To npcs (mean)",
        value=57,
        index=14,
        processing=(IntervalCalculationCategory.to_creatures, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    to_creatures__median: CalculationItem = CalculationItem(
        name="to_creatures__median",
        description="To npcs (median)",
        value=58,
        index=15,
        processing=(IntervalCalculationCategory.to_creatures, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    to_creatures__dmg_inst: CalculationItem = CalculationItem(
        name="to_creatures__dmg_inst",
        description="To npcs (number of instances)",
        value=59,
        index=16,
        processing=(IntervalCalculationCategory.to_creatures, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_illusions__sum: CalculationItem = CalculationItem(
        name="to_illusions__sum",
        description="To illusions (total)",
        value=60,
        index=17,
        processing=(IntervalCalculationCategory.to_illusions, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_illusions__mean: CalculationItem = CalculationItem(
        name="to_illusions__mean",
        description="To illusions (mean)",
        value=61,
        index=18,
        processing=(IntervalCalculationCategory.to_illusions, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    to_illusions__median: CalculationItem = CalculationItem(
        name="to_illusions__median",
        description="To illusions (median)",
        value=62,
        index=19,
        processing=(IntervalCalculationCategory.to_illusions, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    to_illusions__dmg_inst: CalculationItem = CalculationItem(
        name="to_illusions__dmg_inst",
        description="To illusions (number of instances)",
        value=63,
        index=20,
        processing=(IntervalCalculationCategory.to_illusions, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_all__sum: CalculationItem = CalculationItem(
        name="to_all__sum",
        description="Dealt to all (total)",
        value=64,
        index=21,
        processing=(IntervalCalculationCategory.to_all, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    to_all__mean: CalculationItem = CalculationItem(
        name="to_all__mean",
        description="Dealt to all (mean)",
        value=65,
        index=22,
        processing=(IntervalCalculationCategory.to_all, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    to_all__median: CalculationItem = CalculationItem(
        name="to_all__median",
        description="Dealt to all (median)",
        value=66,
        index=23,
        processing=(IntervalCalculationCategory.to_all, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    to_all__dmg_inst: CalculationItem = CalculationItem(
        name="to_all__dmg_inst",
        description="Dealt to all (number of instances)",
        value=67,
        index=24,
        processing=(IntervalCalculationCategory.to_all, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_heroes__sum: CalculationItem = CalculationItem(
        name="from_heroes__sum",
        description="From heroes (total)",
        value=68,
        index=25,
        processing=(IntervalCalculationCategory.from_heroes, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_heroes__mean: CalculationItem = CalculationItem(
        name="from_heroes__mean",
        description="From heroes (mean)",
        value=69,
        index=26,
        processing=(IntervalCalculationCategory.from_heroes, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    from_heroes__median: CalculationItem = CalculationItem(
        name="from_heroes__median",
        description="From heroes (median)",
        value=70,
        index=27,
        processing=(IntervalCalculationCategory.from_heroes, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    from_heroes__dmg_inst: CalculationItem = CalculationItem(
        name="from_heroes__dmg_inst",
        description="From heroes (number of instances)",
        value=71,
        index=28,
        processing=(IntervalCalculationCategory.from_heroes, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_buildings__sum: CalculationItem = CalculationItem(
        name="from_buildings__sum",
        description="From buildings (total)",
        value=72,
        index=29,
        processing=(IntervalCalculationCategory.from_buildings, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_buildings__mean: CalculationItem = CalculationItem(
        name="from_buildings__mean",
        description="From buildings (mean)",
        value=73,
        index=30,
        processing=(IntervalCalculationCategory.from_buildings, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    from_buildings__median: CalculationItem = CalculationItem(
        name="from_buildings__median",
        description="From buildings (median)",
        value=74,
        index=31,
        processing=(IntervalCalculationCategory.from_buildings, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    from_buildings__dmg_inst: CalculationItem = CalculationItem(
        name="from_buildings__dmg_inst",
        description="From buildings (number of instances)",
        value=75,
        index=32,
        processing=(IntervalCalculationCategory.from_buildings, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_creatures__sum: CalculationItem = CalculationItem(
        name="from_creatures__sum",
        description="From npcs (total)",
        value=76,
        index=33,
        processing=(IntervalCalculationCategory.from_creatures, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_creatures__mean: CalculationItem = CalculationItem(
        name="from_creatures__mean",
        description="From npcs (mean)",
        value=77,
        index=34,
        processing=(IntervalCalculationCategory.from_creatures, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    from_creatures__median: CalculationItem = CalculationItem(
        name="from_creatures__median",
        description="From npcs (median)",
        value=78,
        index=35,
        processing=(IntervalCalculationCategory.from_creatures, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    from_creatures__dmg_inst: CalculationItem = CalculationItem(
        name="from_creatures__dmg_inst",
        description="From npcs (number of instances)",
        value=79,
        index=36,
        processing=(IntervalCalculationCategory.from_creatures, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_illusions__sum: CalculationItem = CalculationItem(
        name="from_illusions__sum",
        description="From illusions (total)",
        value=80,
        index=37,
        processing=(IntervalCalculationCategory.from_illusions, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_illusions__mean: CalculationItem = CalculationItem(
        name="from_illusions__mean",
        description="From illusions (mean)",
        value=81,
        index=38,
        processing=(IntervalCalculationCategory.from_illusions, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    from_illusions__median: CalculationItem = CalculationItem(
        name="from_illusions__median",
        description="From illusions (median)",
        value=82,
        index=39,
        processing=(IntervalCalculationCategory.from_illusions, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    from_illusions__dmg_inst: CalculationItem = CalculationItem(
        name="from_illusions__dmg_inst",
        description="From illusions (number of instances)",
        value=83,
        index=40,
        processing=(IntervalCalculationCategory.from_illusions, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_all__sum: CalculationItem = CalculationItem(
        name="from_all__sum",
        description="Received from all (total)",
        value=84,
        index=41,
        processing=(IntervalCalculationCategory.from_all, IntervalCalculationMethod.sum),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )
    from_all__mean: CalculationItem = CalculationItem(
        name="from_all__mean",
        description="Received from all (mean)",
        value=85,
        index=42,
        processing=(IntervalCalculationCategory.from_all, IntervalCalculationMethod.mean),
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
    )
    from_all__median: CalculationItem = CalculationItem(
        name="from_all__median",
        description="Received from all (median)",
        value=86,
        index=43,
        processing=(IntervalCalculationCategory.from_all, IntervalCalculationMethod.median),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
    )
    from_all__dmg_inst: CalculationItem = CalculationItem(
        name="from_all__dmg_inst",
        description="Received from all (number of instances)",
        value=87,
        index=44,
        processing=(IntervalCalculationCategory.from_all, IntervalCalculationMethod.dmg_inst),
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
    )

    VALUES: list[CalculationItem]
