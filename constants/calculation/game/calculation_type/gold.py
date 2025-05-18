from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, \
    add_values
from constants.calculation.game.category import WindowCategories


@add_values
@set_category_and_value(WindowCategories.GOLD)
class GoldCalculations:
    death_penalty: CalculationItem = CalculationItem(
        name="death_penalty",
        description="Gold removed for death",
        index=1,

    )
    death_penalty_pm: CalculationItem = CalculationItem(
        name="death_penalty_pm",
        description="Gold removed for death (per minute)",
        index=2,

    )
    gold_for_assist: CalculationItem = CalculationItem(
        name="gold_for_assist",
        description="Gold for assists",
        index=3,

    )
    gold_for_assist_pm: CalculationItem = CalculationItem(
        name="gold_for_assist_pm",
        description="Gold for assists (per minute)",
        index=4,

    )
    gold_for_killing_buildings: CalculationItem = CalculationItem(
        name="gold_for_killing_buildings",
        description="Gold for killing buildings",
        index=5,

    )
    gold_for_killing_buildings_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_buildings_pm",
        description="Gold for killing buildings (per minute)",
        index=6,

    )
    gold_for_killing_heroes: CalculationItem = CalculationItem(
        name="gold_for_killing_heroes",
        description="Gold for killing heroes",
        index=7,

    )
    gold_for_killing_heroes_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_heroes_pm",
        description="Gold for killing heroes (per minute)",
        index=8,

    )
    gold_for_killing_creeps: CalculationItem = CalculationItem(
        name="gold_for_killing_creeps",
        description="Gold for killing creeps",
        index=9,

    )
    gold_for_killing_creeps_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_creeps_pm",
        description="Gold for killing creeps (per minute)",
        index=10,

    )
    gold_for_killing_neutrals: CalculationItem = CalculationItem(
        name="gold_for_killing_neutrals",
        description="Gold for killing neutrals",
        index=11,

    )
    gold_for_killing_neutrals_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_neutrals_pm",
        description="Gold for killing neutrals (per minute)",
        index=12,

    )
    gold_for_killing_roshan: CalculationItem = CalculationItem(
        name="gold_for_killing_roshan",
        description="Gold for killing roshan",
        index=13,

    )
    gold_for_killing_roshan_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_roshan_pm",
        description="Gold for killing roshan (per minute)",
        index=14,

    )
    gold_for_assisting_killing_couriers: CalculationItem = CalculationItem(
        name="gold_for_assisting_killing_couriers",
        description="Gold for courier assists",
        index=15,

    )
    gold_for_assisting_killing_couriers_pm: CalculationItem = CalculationItem(
        name="gold_for_assisting_killing_couriers_pm",
        description="Gold for courier assists (per minute)",
        index=16,

    )
    gold_runes: CalculationItem = CalculationItem(
        name="gold_runes",
        description="Gold for runes",
        index=17,

    )
    gold_runes_pm: CalculationItem = CalculationItem(
        name="gold_runes_pm",
        description="Gold for runes (per minute)",
        index=18,

    )
    gold_for_flag_bearer_and_dooms_devour: CalculationItem = CalculationItem(
        name="gold_for_flag_bearer_and_doom's_devour",
        description="Gold for flag bearers, devour, etc",
        index=19,

    )
    gold_for_flag_bearer_and_dooms_devour_pm: CalculationItem = CalculationItem(
        name="gold_for_flag_bearer_and_doom's_devour_pm",
        description="Gold for flag bearers, devour, etc (per minute)",
        index=20,

    )
    gold_for_wards: CalculationItem = CalculationItem(
        name="gold_for_wards",
        description="Gold for wards",
        index=21,

    )
    gold_for_wards_pm: CalculationItem = CalculationItem(
        name="gold_for_wards_pm",
        description="Gold for wards (per minute)",
        index=22,

    )
    gold_for_killing_couriers: CalculationItem = CalculationItem(
        name="gold_for_killing_couriers",
        description="Gold for couriers",
        index=23,

    )
    gold_for_killing_couriers_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_couriers_pm",
        description="Gold for couriers (per minute)",
        index=24,

    )

    VALUES: list[CalculationItem]
    VALUES_NAMES: list[str]
