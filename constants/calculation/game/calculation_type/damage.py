from enum import IntEnum

from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, add_values
from constants.calculation.game.category import WindowCategories


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


@add_values
@set_category_and_value(WindowCategories.DAMAGE)
class DamageCalculations:
    with_summons__sum: CalculationItem = CalculationItem(
        name="with_summons__sum",
        description="With summons (total)",
        index=1,
        processing=(IntervalCalculationCategory.with_summons, IntervalCalculationMethod.sum),

    )
    with_summons__mean: CalculationItem = CalculationItem(
        name="with_summons__mean",
        description="With summons (mean)",
        index=2,
        processing=(IntervalCalculationCategory.with_summons, IntervalCalculationMethod.mean),

    )
    with_summons__median: CalculationItem = CalculationItem(
        name="with_summons__median",
        description="With summons (median)",
        index=3,
        processing=(IntervalCalculationCategory.with_summons, IntervalCalculationMethod.median),


    )
    with_summons__dmg_inst: CalculationItem = CalculationItem(
        name="with_summons__dmg_inst",
        description="With summons (number of instances)",
        index=4,
        processing=(IntervalCalculationCategory.with_summons, IntervalCalculationMethod.dmg_inst),

    )
    to_heroes__sum: CalculationItem = CalculationItem(
        name="to_heroes__sum",
        description="To heroes (total)",
        index=5,
        processing=(IntervalCalculationCategory.to_heroes, IntervalCalculationMethod.sum),

    )
    to_heroes__mean: CalculationItem = CalculationItem(
        name="to_heroes__mean",
        description="To heroes (mean)",
        index=6,
        processing=(IntervalCalculationCategory.to_heroes, IntervalCalculationMethod.mean),

    )
    to_heroes__median: CalculationItem = CalculationItem(
        name="to_heroes__median",
        description="To heroes (median)",
        index=7,
        processing=(IntervalCalculationCategory.to_heroes, IntervalCalculationMethod.median),

    )
    to_heroes__dmg_inst: CalculationItem = CalculationItem(
        name="to_heroes__dmg_inst",
        description="To heroes (number of instances)",
        index=8,
        processing=(IntervalCalculationCategory.to_heroes, IntervalCalculationMethod.dmg_inst),

    )
    to_buildings__sum: CalculationItem = CalculationItem(
        name="to_buildings__sum",
        description="To buildings (total)",
        index=9,
        processing=(IntervalCalculationCategory.to_buildings, IntervalCalculationMethod.sum),

    )
    to_buildings__mean: CalculationItem = CalculationItem(
        name="to_buildings__mean",
        description="To buildings (mean)",
        index=10,
        processing=(IntervalCalculationCategory.to_buildings, IntervalCalculationMethod.mean),

    )
    to_buildings__median: CalculationItem = CalculationItem(
        name="to_buildings__median",
        description="To buildings (median)",
        index=11,
        processing=(IntervalCalculationCategory.to_buildings, IntervalCalculationMethod.median),

    )
    to_buildings__dmg_inst: CalculationItem = CalculationItem(
        name="to_buildings__dmg_inst",
        description="To buildings (number of instances)",
        index=12,
        processing=(IntervalCalculationCategory.to_buildings, IntervalCalculationMethod.dmg_inst),

    )
    to_creatures__sum: CalculationItem = CalculationItem(
        name="to_creatures__sum",
        description="To npcs (total)",
        index=13,
        processing=(IntervalCalculationCategory.to_creatures, IntervalCalculationMethod.sum),

    )
    to_creatures__mean: CalculationItem = CalculationItem(
        name="to_creatures__mean",
        description="To npcs (mean)",
        index=14,
        processing=(IntervalCalculationCategory.to_creatures, IntervalCalculationMethod.mean),

    )
    to_creatures__median: CalculationItem = CalculationItem(
        name="to_creatures__median",
        description="To npcs (median)",
        index=15,
        processing=(IntervalCalculationCategory.to_creatures, IntervalCalculationMethod.median),

    )
    to_creatures__dmg_inst: CalculationItem = CalculationItem(
        name="to_creatures__dmg_inst",
        description="To npcs (number of instances)",
        index=16,
        processing=(IntervalCalculationCategory.to_creatures, IntervalCalculationMethod.dmg_inst),

    )
    to_illusions__sum: CalculationItem = CalculationItem(
        name="to_illusions__sum",
        description="To illusions (total)",
        index=17,
        processing=(IntervalCalculationCategory.to_illusions, IntervalCalculationMethod.sum),

    )
    to_illusions__mean: CalculationItem = CalculationItem(
        name="to_illusions__mean",
        description="To illusions (mean)",
        index=18,
        processing=(IntervalCalculationCategory.to_illusions, IntervalCalculationMethod.mean),

    )
    to_illusions__median: CalculationItem = CalculationItem(
        name="to_illusions__median",
        description="To illusions (median)",
        index=19,
        processing=(IntervalCalculationCategory.to_illusions, IntervalCalculationMethod.median),

    )
    to_illusions__dmg_inst: CalculationItem = CalculationItem(
        name="to_illusions__dmg_inst",
        description="To illusions (number of instances)",
        index=20,
        processing=(IntervalCalculationCategory.to_illusions, IntervalCalculationMethod.dmg_inst),

    )
    to_all__sum: CalculationItem = CalculationItem(
        name="to_all__sum",
        description="Dealt to all (total)",
        index=21,
        processing=(IntervalCalculationCategory.to_all, IntervalCalculationMethod.sum),

    )
    to_all__mean: CalculationItem = CalculationItem(
        name="to_all__mean",
        description="Dealt to all (mean)",
        index=22,
        processing=(IntervalCalculationCategory.to_all, IntervalCalculationMethod.mean),

    )
    to_all__median: CalculationItem = CalculationItem(
        name="to_all__median",
        description="Dealt to all (median)",
        index=23,
        processing=(IntervalCalculationCategory.to_all, IntervalCalculationMethod.median),

    )
    to_all__dmg_inst: CalculationItem = CalculationItem(
        name="to_all__dmg_inst",
        description="Dealt to all (number of instances)",
        index=24,
        processing=(IntervalCalculationCategory.to_all, IntervalCalculationMethod.dmg_inst),

    )
    from_heroes__sum: CalculationItem = CalculationItem(
        name="from_heroes__sum",
        description="From heroes (total)",
        index=25,
        processing=(IntervalCalculationCategory.from_heroes, IntervalCalculationMethod.sum),

    )
    from_heroes__mean: CalculationItem = CalculationItem(
        name="from_heroes__mean",
        description="From heroes (mean)",
        index=26,
        processing=(IntervalCalculationCategory.from_heroes, IntervalCalculationMethod.mean),

    )
    from_heroes__median: CalculationItem = CalculationItem(
        name="from_heroes__median",
        description="From heroes (median)",
        index=27,
        processing=(IntervalCalculationCategory.from_heroes, IntervalCalculationMethod.median),

    )
    from_heroes__dmg_inst: CalculationItem = CalculationItem(
        name="from_heroes__dmg_inst",
        description="From heroes (number of instances)",
        index=28,
        processing=(IntervalCalculationCategory.from_heroes, IntervalCalculationMethod.dmg_inst),

    )
    from_buildings__sum: CalculationItem = CalculationItem(
        name="from_buildings__sum",
        description="From buildings (total)",
        index=29,
        processing=(IntervalCalculationCategory.from_buildings, IntervalCalculationMethod.sum),

    )
    from_buildings__mean: CalculationItem = CalculationItem(
        name="from_buildings__mean",
        description="From buildings (mean)",
        index=30,
        processing=(IntervalCalculationCategory.from_buildings, IntervalCalculationMethod.mean),

    )
    from_buildings__median: CalculationItem = CalculationItem(
        name="from_buildings__median",
        description="From buildings (median)",
        index=31,
        processing=(IntervalCalculationCategory.from_buildings, IntervalCalculationMethod.median),

    )
    from_buildings__dmg_inst: CalculationItem = CalculationItem(
        name="from_buildings__dmg_inst",
        description="From buildings (number of instances)",
        index=32,
        processing=(IntervalCalculationCategory.from_buildings, IntervalCalculationMethod.dmg_inst),

    )
    from_creatures__sum: CalculationItem = CalculationItem(
        name="from_creatures__sum",
        description="From npcs (total)",
        index=33,
        processing=(IntervalCalculationCategory.from_creatures, IntervalCalculationMethod.sum),

    )
    from_creatures__mean: CalculationItem = CalculationItem(
        name="from_creatures__mean",
        description="From npcs (mean)",
        index=34,
        processing=(IntervalCalculationCategory.from_creatures, IntervalCalculationMethod.mean),

    )
    from_creatures__median: CalculationItem = CalculationItem(
        name="from_creatures__median",
        description="From npcs (median)",
        index=35,
        processing=(IntervalCalculationCategory.from_creatures, IntervalCalculationMethod.median),

    )
    from_creatures__dmg_inst: CalculationItem = CalculationItem(
        name="from_creatures__dmg_inst",
        description="From npcs (number of instances)",
        index=36,
        processing=(IntervalCalculationCategory.from_creatures, IntervalCalculationMethod.dmg_inst),

    )
    from_illusions__sum: CalculationItem = CalculationItem(
        name="from_illusions__sum",
        description="From illusions (total)",
        index=37,
        processing=(IntervalCalculationCategory.from_illusions, IntervalCalculationMethod.sum),

    )
    from_illusions__mean: CalculationItem = CalculationItem(
        name="from_illusions__mean",
        description="From illusions (mean)",
        index=38,
        processing=(IntervalCalculationCategory.from_illusions, IntervalCalculationMethod.mean),

    )
    from_illusions__median: CalculationItem = CalculationItem(
        name="from_illusions__median",
        description="From illusions (median)",
        index=39,
        processing=(IntervalCalculationCategory.from_illusions, IntervalCalculationMethod.median),

    )
    from_illusions__dmg_inst: CalculationItem = CalculationItem(
        name="from_illusions__dmg_inst",
        description="From illusions (number of instances)",
        index=40,
        processing=(IntervalCalculationCategory.from_illusions, IntervalCalculationMethod.dmg_inst),

    )
    from_all__sum: CalculationItem = CalculationItem(
        name="from_all__sum",
        description="Received from all (total)",
        index=41,
        processing=(IntervalCalculationCategory.from_all, IntervalCalculationMethod.sum),

    )
    from_all__mean: CalculationItem = CalculationItem(
        name="from_all__mean",
        description="Received from all (mean)",
        index=42,
        processing=(IntervalCalculationCategory.from_all, IntervalCalculationMethod.mean),

    )
    from_all__median: CalculationItem = CalculationItem(
        name="from_all__median",
        description="Received from all (median)",
        index=43,
        processing=(IntervalCalculationCategory.from_all, IntervalCalculationMethod.median),

    )
    from_all__dmg_inst: CalculationItem = CalculationItem(
        name="from_all__dmg_inst",
        description="Received from all (number of instances)",
        index=44,
        processing=(IntervalCalculationCategory.from_all, IntervalCalculationMethod.dmg_inst),

    )

    VALUES: list[CalculationItem]
    VALUES_NAMES: list[str]
