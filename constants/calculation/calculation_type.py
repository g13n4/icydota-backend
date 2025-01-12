from typing import ClassVar, Callable, TypeVar

from pydantic import BaseModel
from sqlmodel import Field

from constants.calculation.category import WindowCategories
from constants.helpers import Item, GetItemHelper


CalculationType = TypeVar('CalculationType')


def set_category(category: Item) -> Callable:
    def decorator(klass: object) -> object:
        for name, type_ in klass.__annotations__.items():
            item = getattr(klass, name)
            item.category = category
        return klass

    return decorator


class IntervalCalculationCategory(GetItemHelper):
    TEAMFIGHT_PARTICIPATION: ClassVar[int] = 1
    MOVEMENT: ClassVar[int] = 2
    LH: ClassVar[int] = 3
    XP: ClassVar[int] = 4
    STACKED: ClassVar[int] = 5
    ROSHANS_KILLED: ClassVar[int] = 6
    SEN_PLACED: ClassVar[int] = 7
    GOLD: ClassVar[int] = 8
    DEATHS: ClassVar[int] = 9
    TOWERS_KILLED: ClassVar[int] = 10
    RUNE_PICKUPS: ClassVar[int] = 11
    KDA: ClassVar[int] = 12
    NETWORTH: ClassVar[int] = 13
    OBS_PLACED: ClassVar[int] = 14
    KILLS: ClassVar[int] = 15
    LEVEL: ClassVar[int] = 16


class IntervalCalculationType(GetItemHelper):
    MIN: ClassVar[int] = 1
    AVG: ClassVar[int] = 2
    MAX: ClassVar[int] = 3
    SUM: ClassVar[int] = 4

    GAINED_PW: ClassVar[int] = 5

    GAINED_PM_MEDIAN: ClassVar[int] = 6
    MAX_GLOBAL_PERC: ClassVar[int] = 7
    AVG_BY_LENGTH_PM: ClassVar[int] = 8



class PostprocessingItem(BaseModel):
    carry_comparison: bool = False
    support_comparison: bool = False

    percentage: bool = False

    max_total: bool = False
    sum_total: bool = False
    average_total: bool = False



class CalculationItem(BaseModel):
    name: str
    description: str
    value: int
    index: int
    category: Item | None = None
    calculation: tuple[int, int] | None = None
    active: bool = True
    postprocessing: PostprocessingItem = Field(default_factory=PostprocessingItem)


def add_values(klass: CalculationType) -> CalculationType:
    VALUES = []
    for name, type_ in klass.__annotations__.items():
        if isinstance(type_, CalculationItem):
            value = getattr(klass, name)
            VALUES.append(value)

    setattr(klass, 'VALUES', VALUES)
    return klass

@add_values
@set_category(WindowCategories.INTERVAL)
class IntervalCalculations:
    gold__max: CalculationItem = CalculationItem(
        name="gold__max",
        description="Gold",
        value=1,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.GOLD, IntervalCalculationType.MAX),
    )
    gold__gained_pm_median: CalculationItem = CalculationItem(
        name="gold__gained_pm_median",
        description="Gold median (per minute)",
        value=2,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.GOLD, IntervalCalculationType.GAINED_PM_MEDIAN),
    )
    gold__gained_pw: CalculationItem = CalculationItem(
        name="gold__gained_pw",
        description="Gold gained",
        value=3,
        index=3,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.GOLD, IntervalCalculationType.GAINED_PW),
    )
    gold__avg_by_length_pm: CalculationItem = CalculationItem(
        name="gold__avg_by_length_pm",
        description="GPM",
        value=4,
        index=4,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.GOLD, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    gold__max_global_perc: CalculationItem = CalculationItem(
        name="gold__max_global_perc",
        description="Gold control (total%)",
        value=5,
        index=5,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.GOLD, IntervalCalculationType.MAX_GLOBAL_PERC),
    )
    xp__max: CalculationItem = CalculationItem(
        name="xp__max",
        description="XP",
        value=6,
        index=6,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.XP, IntervalCalculationType.MAX),
    )
    xp__gained_pm_median: CalculationItem = CalculationItem(
        name="xp__gained_pm_median",
        description="XP median (per minute)",
        value=7,
        index=7,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.XP, IntervalCalculationType.GAINED_PM_MEDIAN),
    )
    xp__gained_pw: CalculationItem = CalculationItem(
        name="xp__gained_pw",
        description="XP gained",
        value=8,
        index=8,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.XP, IntervalCalculationType.GAINED_PW),
    )
    xp__avg_by_length_pm: CalculationItem = CalculationItem(
        name="xp__avg_by_length_pm",
        description="XPM",
        value=9,
        index=9,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.XP, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    xp__max_global_perc: CalculationItem = CalculationItem(
        name="xp__max_global_perc",
        description="XP control (total%)",
        value=10,
        index=10,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.XP, IntervalCalculationType.MAX_GLOBAL_PERC),
    )
    lh__max: CalculationItem = CalculationItem(
        name="lh__max",
        description="Last hits",
        value=11,
        index=11,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.LH, IntervalCalculationType.MAX),
    )
    lh__gained_pw: CalculationItem = CalculationItem(
        name="lh__gained_pw",
        description="Last hits gained",
        value=12,
        index=12,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.LH, IntervalCalculationType.GAINED_PW),
    )
    lh__avg_by_length_pm: CalculationItem = CalculationItem(
        name="lh__avg_by_length_pm",
        description="Last hits average (per minute)",
        value=13,
        index=13,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.LH, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    movement__sum: CalculationItem = CalculationItem(
        name="movement__sum",
        description="Distance traveled",
        value=14,
        index=14,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    calculation=(IntervalCalculationCategory.MOVEMENT, IntervalCalculationType.SUM),
    )
    movement__avg_by_length_pm: CalculationItem = CalculationItem(
        name="movement__avg_by_length_pm",
        description="Distance traveled (per minute)",
        value=15,
        index=15,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.MOVEMENT, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    level__max: CalculationItem = CalculationItem(
        name="level__max",
        description="Level",
        value=16,
        index=16,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.LEVEL, IntervalCalculationType.MAX),
    )
    level__gained_pw: CalculationItem = CalculationItem(
        name="level__gained_pw",
        description="Levels gained",
        value=17,
        index=17,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.LEVEL, IntervalCalculationType.GAINED_PW),
    )
    kills__max: CalculationItem = CalculationItem(
        name="kills__max",
        description="Kills",
        value=18,
        index=18,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.KILLS, IntervalCalculationType.MAX),
    )
    kills__avg_by_length_pm: CalculationItem = CalculationItem(
        name="kills__avg_by_length_pm",
        description="Kills average (per minute)",
        value=19,
        index=19,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.KILLS, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    kills__max_global_perc: CalculationItem = CalculationItem(
        name="kills__max_global_perc",
        description="Kills control (total%)",
        value=20,
        index=20,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.KILLS, IntervalCalculationType.MAX_GLOBAL_PERC),
    )
    deaths__max: CalculationItem = CalculationItem(
        name="deaths__max",
        description="Deaths",
        value=21,
        index=21,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.DEATHS, IntervalCalculationType.MAX),
    )
    deaths__avg_by_length_pm: CalculationItem = CalculationItem(
        name="deaths__avg_by_length_pm",
        description="Deaths average (per minute)",
        value=22,
        index=22,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.DEATHS, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    deaths__max_global_perc: CalculationItem = CalculationItem(
        name="deaths__max_global_perc",
        description="Deaths control (total%)",
        value=23,
        index=23,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.DEATHS, IntervalCalculationType.MAX_GLOBAL_PERC),
    )
    kda__max: CalculationItem = CalculationItem(
        name="kda__max",
        description="KDA",
        value=24,
        index=24,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.KDA, IntervalCalculationType.MAX),
    )
    kda__avg_by_length_pm: CalculationItem = CalculationItem(
        name="kda__avg_by_length_pm",
        description="KDA average (per minute)",
        value=25,
        index=25,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.KDA, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    kda__gained_pw: CalculationItem = CalculationItem(
        name="kda__gained_pw",
        description="KDA gained",
        value=26,
        index=26,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.KDA, IntervalCalculationType.GAINED_PW),
    )
    obs_placed__max: CalculationItem = CalculationItem(
        name="obs_placed__max",
        description="Observer wards placed",
        value=27,
        index=27,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.OBS_PLACED, IntervalCalculationType.MAX),
    )
    obs_placed__avg_by_length_pm: CalculationItem = CalculationItem(
        name="obs_placed__avg_by_length_pm",
        description="Observer wards placed (per minute)",
        value=28,
        index=28,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.OBS_PLACED, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    sen_placed__max: CalculationItem = CalculationItem(
        name="sen_placed__max",
        description="Sentry wards placed",
        value=29,
        index=29,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.SEN_PLACED, IntervalCalculationType.MAX),
    )
    sen_placed__avg_by_length_pm: CalculationItem = CalculationItem(
        name="sen_placed__avg_by_length_pm",
        description="Sentry wards placed (per minute)",
        value=30,
        index=30,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.SEN_PLACED, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    stacked__max: CalculationItem = CalculationItem(
        name="stacked__max",
        description="Stacked",
        value=31,
        index=31,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.STACKED, IntervalCalculationType.MAX),
    )
    stacked__avg_by_length_pm: CalculationItem = CalculationItem(
        name="stacked__avg_by_length_pm",
        description="Stacked average (per minute)",
        value=32,
        index=32,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.STACKED, IntervalCalculationType.AVG_BY_LENGTH_PM),
    )
    rune_pickups__max: CalculationItem = CalculationItem(
        name="rune_pickups__max",
        description="Runes picked up",
        value=33,
        index=33,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    calculation=(IntervalCalculationCategory.RUNE_PICKUPS, IntervalCalculationType.MAX),
    )
    teamfight_participation__avg: CalculationItem = CalculationItem(
        name="teamfight_participation__avg",
        description="Team fight participation average",
        value=34,
        index=34,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.TEAMFIGHT_PARTICIPATION, IntervalCalculationType.AVG),
    )
    teamfight_participation__max: CalculationItem = CalculationItem(
        name="teamfight_participation__max",
        description="Team fight participation max",
        value=35,
        index=35,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.TEAMFIGHT_PARTICIPATION, IntervalCalculationType.MAX),
    )
    teamfight_participation__min: CalculationItem = CalculationItem(
        name="teamfight_participation__min",
        description="Team fight participation min",
        value=36,
        index=36,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.TEAMFIGHT_PARTICIPATION, IntervalCalculationType.MIN),
    )
    towers_killed__max: CalculationItem = CalculationItem(
        name="towers_killed__max",
        description="Towers kills",
        value=37,
        index=37,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.TOWERS_KILLED, IntervalCalculationType.MAX),
    )
    towers_killed__gained_pw: CalculationItem = CalculationItem(
        name="towers_killed__gained_pw",
        description="Towers kills gained (per minute)",
        value=38,
        index=38,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.TOWERS_KILLED, IntervalCalculationType.GAINED_PW),
    )
    roshans_killed__max: CalculationItem = CalculationItem(
        name="roshans_killed__max",
        description="Roshan kills",
        value=39,
        index=39,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.ROSHANS_KILLED, IntervalCalculationType.MAX),
    )
    networth__max: CalculationItem = CalculationItem(
        name="networth__max",
        description="Networth",
        value=40,
        index=40,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=True, sum_total=False, average_total=False),
    calculation=(IntervalCalculationCategory.NETWORTH, IntervalCalculationType.MAX),
    )
    networth__gained_pw: CalculationItem = CalculationItem(
        name="networth__gained_pw",
        description="Networth gained",
        value=41,
        index=41,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    calculation=(IntervalCalculationCategory.NETWORTH, IntervalCalculationType.GAINED_PW),
    )


@add_values
@set_category(WindowCategories.PINGS)
class PingsCalculations:
    pings: CalculationItem = CalculationItem(
        name="pings",
        description="Pings",
        value=42,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    pings_per_minute: CalculationItem = CalculationItem(
        name="pings_per_minute",
        description="Pings (per minute)",
        value=43,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )


@set_category(WindowCategories.DAMAGE)
class DamageCalculations:
    with_summons__sum: CalculationItem = CalculationItem(
        name="with_summons__sum",
        description="With summons (total)",
        value=44,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    with_summons__mean: CalculationItem = CalculationItem(
        name="with_summons__mean",
        description="With summons (mean)",
        value=45,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    with_summons__median: CalculationItem = CalculationItem(
        name="with_summons__median",
        description="With summons (median)",
        value=46,
        index=3,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    with_summons__dmg_inst: CalculationItem = CalculationItem(
        name="with_summons__dmg_inst",
        description="With summons (number of instances)",
        value=47,
        index=4,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_heroes__sum: CalculationItem = CalculationItem(
        name="to_heroes__sum",
        description="To heroes (total)",
        value=48,
        index=5,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_heroes__mean: CalculationItem = CalculationItem(
        name="to_heroes__mean",
        description="To heroes (mean)",
        value=49,
        index=6,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    to_heroes__median: CalculationItem = CalculationItem(
        name="to_heroes__median",
        description="To heroes (median)",
        value=50,
        index=7,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    to_heroes__dmg_inst: CalculationItem = CalculationItem(
        name="to_heroes__dmg_inst",
        description="To heroes (number of instances)",
        value=51,
        index=8,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_buildings__sum: CalculationItem = CalculationItem(
        name="to_buildings__sum",
        description="To buildings (total)",
        value=52,
        index=9,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_buildings__mean: CalculationItem = CalculationItem(
        name="to_buildings__mean",
        description="To buildings (mean)",
        value=53,
        index=10,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    to_buildings__median: CalculationItem = CalculationItem(
        name="to_buildings__median",
        description="To buildings (median)",
        value=54,
        index=11,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    to_buildings__dmg_inst: CalculationItem = CalculationItem(
        name="to_buildings__dmg_inst",
        description="To buildings (number of instances)",
        value=55,
        index=12,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_creatures__sum: CalculationItem = CalculationItem(
        name="to_creatures__sum",
        description="To npcs (total)",
        value=56,
        index=13,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_creatures__mean: CalculationItem = CalculationItem(
        name="to_creatures__mean",
        description="To npcs (mean)",
        value=57,
        index=14,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    to_creatures__median: CalculationItem = CalculationItem(
        name="to_creatures__median",
        description="To npcs (median)",
        value=58,
        index=15,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    to_creatures__dmg_inst: CalculationItem = CalculationItem(
        name="to_creatures__dmg_inst",
        description="To npcs (number of instances)",
        value=59,
        index=16,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_illusions__sum: CalculationItem = CalculationItem(
        name="to_illusions__sum",
        description="To illusions (total)",
        value=60,
        index=17,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_illusions__mean: CalculationItem = CalculationItem(
        name="to_illusions__mean",
        description="To illusions (mean)",
        value=61,
        index=18,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    to_illusions__median: CalculationItem = CalculationItem(
        name="to_illusions__median",
        description="To illusions (median)",
        value=62,
        index=19,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    to_illusions__dmg_inst: CalculationItem = CalculationItem(
        name="to_illusions__dmg_inst",
        description="To illusions (number of instances)",
        value=63,
        index=20,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_all__sum: CalculationItem = CalculationItem(
        name="to_all__sum",
        description="Dealt to all (total)",
        value=64,
        index=21,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    to_all__mean: CalculationItem = CalculationItem(
        name="to_all__mean",
        description="Dealt to all (mean)",
        value=65,
        index=22,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    to_all__median: CalculationItem = CalculationItem(
        name="to_all__median",
        description="Dealt to all (median)",
        value=66,
        index=23,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    to_all__dmg_inst: CalculationItem = CalculationItem(
        name="to_all__dmg_inst",
        description="Dealt to all (number of instances)",
        value=67,
        index=24,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_heroes__sum: CalculationItem = CalculationItem(
        name="from_heroes__sum",
        description="From heroes (total)",
        value=68,
        index=25,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_heroes__mean: CalculationItem = CalculationItem(
        name="from_heroes__mean",
        description="From heroes (mean)",
        value=69,
        index=26,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    from_heroes__median: CalculationItem = CalculationItem(
        name="from_heroes__median",
        description="From heroes (median)",
        value=70,
        index=27,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    from_heroes__dmg_inst: CalculationItem = CalculationItem(
        name="from_heroes__dmg_inst",
        description="From heroes (number of instances)",
        value=71,
        index=28,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_buildings__sum: CalculationItem = CalculationItem(
        name="from_buildings__sum",
        description="From buildings (total)",
        value=72,
        index=29,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_buildings__mean: CalculationItem = CalculationItem(
        name="from_buildings__mean",
        description="From buildings (mean)",
        value=73,
        index=30,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    from_buildings__median: CalculationItem = CalculationItem(
        name="from_buildings__median",
        description="From buildings (median)",
        value=74,
        index=31,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    from_buildings__dmg_inst: CalculationItem = CalculationItem(
        name="from_buildings__dmg_inst",
        description="From buildings (number of instances)",
        value=75,
        index=32,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_creatures__sum: CalculationItem = CalculationItem(
        name="from_creatures__sum",
        description="From npcs (total)",
        value=76,
        index=33,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_creatures__mean: CalculationItem = CalculationItem(
        name="from_creatures__mean",
        description="From npcs (mean)",
        value=77,
        index=34,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    from_creatures__median: CalculationItem = CalculationItem(
        name="from_creatures__median",
        description="From npcs (median)",
        value=78,
        index=35,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    from_creatures__dmg_inst: CalculationItem = CalculationItem(
        name="from_creatures__dmg_inst",
        description="From npcs (number of instances)",
        value=79,
        index=36,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_illusions__sum: CalculationItem = CalculationItem(
        name="from_illusions__sum",
        description="From illusions (total)",
        value=80,
        index=37,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_illusions__mean: CalculationItem = CalculationItem(
        name="from_illusions__mean",
        description="From illusions (mean)",
        value=81,
        index=38,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    from_illusions__median: CalculationItem = CalculationItem(
        name="from_illusions__median",
        description="From illusions (median)",
        value=82,
        index=39,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    from_illusions__dmg_inst: CalculationItem = CalculationItem(
        name="from_illusions__dmg_inst",
        description="From illusions (number of instances)",
        value=83,
        index=40,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_all__sum: CalculationItem = CalculationItem(
        name="from_all__sum",
        description="Received from all (total)",
        value=84,
        index=41,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )
    from_all__mean: CalculationItem = CalculationItem(
        name="from_all__mean",
        description="Received from all (mean)",
        value=85,
        index=42,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    from_all__median: CalculationItem = CalculationItem(
        name="from_all__median",
        description="Received from all (median)",
        value=86,
        index=43,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=False, average_total=True),
    )
    from_all__dmg_inst: CalculationItem = CalculationItem(
        name="from_all__dmg_inst",
        description="Received from all (number of instances)",
        value=87,
        index=44,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, max_total=False, sum_total=True, average_total=False),
    )


@add_values
@set_category(WindowCategories.WARDS)
class WardsCalculations:
    placed_wards_sen: CalculationItem = CalculationItem(
        name="placed_wards_sen",
        description="Placed sentries",
        value=88,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    placed_wards_obs: CalculationItem = CalculationItem(
        name="placed_wards_obs",
        description="Placed observers",
        value=89,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )

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

@add_values
@set_category(WindowCategories.XP)
class XPCalculations:
    other: CalculationItem = CalculationItem(
        name="other",
        description="Other XP",
        value=98,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    xp_for_heroes: CalculationItem = CalculationItem(
        name="xp_for_heroes",
        description="XP for heroes",
        value=99,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    xp_for_heroes_pm: CalculationItem = CalculationItem(
        name="xp_for_heroes_pm",
        description="XP for heroes (per minute)",
        value=100,
        index=3,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    xp_for_creeps: CalculationItem = CalculationItem(
        name="xp_for_creeps",
        description="XP for creeps",
        value=101,
        index=4,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    xp_for_creeps_pm: CalculationItem = CalculationItem(
        name="xp_for_creeps_pm",
        description="XP for creeps (per minute)",
        value=102,
        index=5,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    xp_for_roshan: CalculationItem = CalculationItem(
        name="xp_for_roshan",
        description="XP for roshan",
        value=103,
        index=6,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )


@add_values
@set_category(WindowCategories.GOLD)
class GoldCalculations:
    death_penalty: CalculationItem = CalculationItem(
        name="death_penalty",
        description="Gold removed for death",
        value=104,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    death_penalty_pm: CalculationItem = CalculationItem(
        name="death_penalty_pm",
        description="Gold removed for death (per minute)",
        value=105,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_assist: CalculationItem = CalculationItem(
        name="gold_for_assist",
        description="Gold for assists",
        value=106,
        index=3,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_assist_pm: CalculationItem = CalculationItem(
        name="gold_for_assist_pm",
        description="Gold for assists (per minute)",
        value=107,
        index=4,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_killing_buildings: CalculationItem = CalculationItem(
        name="gold_for_killing_buildings",
        description="Gold for killing buildings",
        value=108,
        index=5,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_killing_buildings_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_buildings_pm",
        description="Gold for killing buildings (per minute)",
        value=109,
        index=6,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_killing_heroes: CalculationItem = CalculationItem(
        name="gold_for_killing_heroes",
        description="Gold for killing heroes",
        value=110,
        index=7,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_killing_heroes_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_heroes_pm",
        description="Gold for killing heroes (per minute)",
        value=111,
        index=8,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_killing_creeps: CalculationItem = CalculationItem(
        name="gold_for_killing_creeps",
        description="Gold for killing creeps",
        value=112,
        index=9,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_killing_creeps_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_creeps_pm",
        description="Gold for killing creeps (per minute)",
        value=113,
        index=10,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_killing_neutrals: CalculationItem = CalculationItem(
        name="gold_for_killing_neutrals",
        description="Gold for killing neutrals",
        value=114,
        index=11,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_killing_neutrals_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_neutrals_pm",
        description="Gold for killing neutrals (per minute)",
        value=115,
        index=12,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_killing_roshan: CalculationItem = CalculationItem(
        name="gold_for_killing_roshan",
        description="Gold for killing roshan",
        value=116,
        index=13,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_killing_roshan_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_roshan_pm",
        description="Gold for killing roshan (per minute)",
        value=117,
        index=14,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_assisting_killing_couriers: CalculationItem = CalculationItem(
        name="gold_for_assisting_killing_couriers",
        description="Gold for courier assists",
        value=118,
        index=15,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_assisting_killing_couriers_pm: CalculationItem = CalculationItem(
        name="gold_for_assisting_killing_couriers_pm",
        description="Gold for courier assists (per minute)",
        value=119,
        index=16,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_runes: CalculationItem = CalculationItem(
        name="gold_runes",
        description="Gold for runes",
        value=120,
        index=17,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_runes_pm: CalculationItem = CalculationItem(
        name="gold_runes_pm",
        description="Gold for runes (per minute)",
        value=121,
        index=18,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_flag_bearer_and_dooms_devour: CalculationItem = CalculationItem(
    name = "gold_for_flag_bearer_and_doom's_devour",
    description = "Gold for flag bearers, devour, etc",
    value = 122,
    index = 19,
    postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_flag_bearer_and_dooms_devour_pm: CalculationItem = CalculationItem(
    name = "gold_for_flag_bearer_and_doom's_devour_pm",
    description = "Gold for flag bearers, devour, etc (per minute)",
    value = 123,
    index = 20,
    postprocessing =  PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_wards: CalculationItem = CalculationItem(
        name="gold_for_wards",
        description="Gold for wards",
        value=124,
        index=21,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_wards_pm: CalculationItem = CalculationItem(
        name="gold_for_wards_pm",
        description="Gold for wards (per minute)",
        value=125,
        index=22,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )
    gold_for_killing_couriers: CalculationItem = CalculationItem(
        name="gold_for_killing_couriers",
        description="Gold for couriers",
        value=126,
        index=23,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=True, average_total=False),
    )
    gold_for_killing_couriers_pm: CalculationItem = CalculationItem(
        name="gold_for_killing_couriers_pm",
        description="Gold for couriers (per minute)",
        value=127,
        index=24,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, max_total=False, sum_total=False, average_total=True),
    )


@add_values
class WindowCalculations(
    IntervalCalculations,
    PingsCalculations,
    DamageCalculations,
    WardsCalculations,
    DewardCalculations,
    XPCalculations,
    GoldCalculations
):
    pass
