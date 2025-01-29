from enum import StrEnum, auto, Enum

from constants.calculation.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.calculation_type.helpers import CalculationItem, set_category, PostprocessingItem, add_values
from constants.calculation.category import WindowCategories


class IntervalCalculationColumn(StrEnum):
    TEAMFIGHT_PARTICIPATION = auto()
    MOVEMENT = auto()
    LH = auto()
    XP = auto()
    STACKED = auto()
    ROSHANS_KILLED = auto()
    SEN_PLACED = auto()
    GOLD = auto()
    DEATHS = auto()
    TOWERS_KILLED = auto()
    RUNE_PICKUPS = auto()
    KDA = auto()
    NETWORTH = auto()
    OBS_PLACED = auto()
    KILLS = auto()
    LEVEL = auto()


class IntervalCalculationAggregationMethod(Enum):
    MIN = 1
    AVG = 2
    MAX = 3
    SUM = 4

    GAINED_PW = 5

    GAINED_PM_MEDIAN = 6
    MAX_GLOBAL_PERC = 7
    AVG_BY_LENGTH_PM = 8


@add_values
@set_category(WindowCategories.INTERVAL)
class IntervalCalculations:
    gold__max: CalculationItem = CalculationItem(
        name="gold__max",
        description="Gold",
        value=1,
        index=1,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.MAX),
    )
    gold__gained_pm_median: CalculationItem = CalculationItem(
        name="gold__gained_pm_median",
        description="Gold median (per minute)",
        value=2,
        index=2,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.GAINED_PM_MEDIAN),
    )
    gold__gained_pw: CalculationItem = CalculationItem(
        name="gold__gained_pw",
        description="Gold gained",
        value=3,
        index=3,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    gold__avg_by_length_pm: CalculationItem = CalculationItem(
        name="gold__avg_by_length_pm",
        description="GPM",
        value=4,
        index=4,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    gold__max_global_perc: CalculationItem = CalculationItem(
        name="gold__max_global_perc",
        description="Gold control (total%)",
        value=5,
        index=5,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.MAX_GLOBAL_PERC),
    )
    xp__max: CalculationItem = CalculationItem(
        name="xp__max",
        description="XP",
        value=6,
        index=6,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.MAX),
    )
    xp__gained_pm_median: CalculationItem = CalculationItem(
        name="xp__gained_pm_median",
        description="XP median (per minute)",
        value=7,
        index=7,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.GAINED_PM_MEDIAN),
    )
    xp__gained_pw: CalculationItem = CalculationItem(
        name="xp__gained_pw",
        description="XP gained",
        value=8,
        index=8,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    xp__avg_by_length_pm: CalculationItem = CalculationItem(
        name="xp__avg_by_length_pm",
        description="XPM",
        value=9,
        index=9,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    xp__max_global_perc: CalculationItem = CalculationItem(
        name="xp__max_global_perc",
        description="XP control (total%)",
        value=10,
        index=10,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.MAX_GLOBAL_PERC),
    )
    lh__max: CalculationItem = CalculationItem(
        name="lh__max",
        description="Last hits",
        value=11,
        index=11,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.LH, IntervalCalculationAggregationMethod.MAX),
    )
    lh__gained_pw: CalculationItem = CalculationItem(
        name="lh__gained_pw",
        description="Last hits gained",
        value=12,
        index=12,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.LH, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    lh__avg_by_length_pm: CalculationItem = CalculationItem(
        name="lh__avg_by_length_pm",
        description="Last hits average (per minute)",
        value=13,
        index=13,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.LH, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    movement__sum: CalculationItem = CalculationItem(
        name="movement__sum",
        description="Distance traveled",
        value=14,
        index=14,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
        processing=(IntervalCalculationColumn.MOVEMENT, IntervalCalculationAggregationMethod.SUM),
    )
    movement__avg_by_length_pm: CalculationItem = CalculationItem(
        name="movement__avg_by_length_pm",
        description="Distance traveled (per minute)",
        value=15,
        index=15,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.MOVEMENT, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    level__max: CalculationItem = CalculationItem(
        name="level__max",
        description="Level",
        value=16,
        index=16,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.LEVEL, IntervalCalculationAggregationMethod.MAX),
    )
    level__gained_pw: CalculationItem = CalculationItem(
        name="level__gained_pw",
        description="Levels gained",
        value=17,
        index=17,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.LEVEL, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    kills__max: CalculationItem = CalculationItem(
        name="kills__max",
        description="Kills",
        value=18,
        index=18,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.KILLS, IntervalCalculationAggregationMethod.MAX),
    )
    kills__avg_by_length_pm: CalculationItem = CalculationItem(
        name="kills__avg_by_length_pm",
        description="Kills average (per minute)",
        value=19,
        index=19,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.KILLS, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    kills__max_global_perc: CalculationItem = CalculationItem(
        name="kills__max_global_perc",
        description="Kills control (total%)",
        value=20,
        index=20,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.KILLS, IntervalCalculationAggregationMethod.MAX_GLOBAL_PERC),
    )
    deaths__max: CalculationItem = CalculationItem(
        name="deaths__max",
        description="Deaths",
        value=21,
        index=21,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.DEATHS, IntervalCalculationAggregationMethod.MAX),
    )
    deaths__avg_by_length_pm: CalculationItem = CalculationItem(
        name="deaths__avg_by_length_pm",
        description="Deaths average (per minute)",
        value=22,
        index=22,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.DEATHS, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    deaths__max_global_perc: CalculationItem = CalculationItem(
        name="deaths__max_global_perc",
        description="Deaths control (total%)",
        value=23,
        index=23,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.DEATHS, IntervalCalculationAggregationMethod.MAX_GLOBAL_PERC),
    )
    kda__max: CalculationItem = CalculationItem(
        name="kda__max",
        description="KDA",
        value=24,
        index=24,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.KDA, IntervalCalculationAggregationMethod.MAX),
    )
    kda__avg_by_length_pm: CalculationItem = CalculationItem(
        name="kda__avg_by_length_pm",
        description="KDA average (per minute)",
        value=25,
        index=25,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.KDA, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    kda__gained_pw: CalculationItem = CalculationItem(
        name="kda__gained_pw",
        description="KDA gained",
        value=26,
        index=26,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.KDA, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    obs_placed__max: CalculationItem = CalculationItem(
        name="obs_placed__max",
        description="Observer wards placed",
        value=27,
        index=27,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.OBS_PLACED, IntervalCalculationAggregationMethod.MAX),
    )
    obs_placed__avg_by_length_pm: CalculationItem = CalculationItem(
        name="obs_placed__avg_by_length_pm",
        description="Observer wards placed (per minute)",
        value=28,
        index=28,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.OBS_PLACED, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    sen_placed__max: CalculationItem = CalculationItem(
        name="sen_placed__max",
        description="Sentry wards placed",
        value=29,
        index=29,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.SEN_PLACED, IntervalCalculationAggregationMethod.MAX),
    )
    sen_placed__avg_by_length_pm: CalculationItem = CalculationItem(
        name="sen_placed__avg_by_length_pm",
        description="Sentry wards placed (per minute)",
        value=30,
        index=30,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.SEN_PLACED, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    stacked__max: CalculationItem = CalculationItem(
        name="stacked__max",
        description="Stacked",
        value=31,
        index=31,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.STACKED, IntervalCalculationAggregationMethod.MAX),
    )
    stacked__avg_by_length_pm: CalculationItem = CalculationItem(
        name="stacked__avg_by_length_pm",
        description="Stacked average (per minute)",
        value=32,
        index=32,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.STACKED, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    rune_pickups__max: CalculationItem = CalculationItem(
        name="rune_pickups__max",
        description="Runes picked up",
        value=33,
        index=33,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.SUM),
        processing=(IntervalCalculationColumn.RUNE_PICKUPS, IntervalCalculationAggregationMethod.MAX),
    )
    teamfight_participation__avg: CalculationItem = CalculationItem(
        name="teamfight_participation__avg",
        description="Team fight participation average",
        value=34,
        index=34,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.TEAMFIGHT_PARTICIPATION, IntervalCalculationAggregationMethod.AVG),
    )
    teamfight_participation__max: CalculationItem = CalculationItem(
        name="teamfight_participation__max",
        description="Team fight participation max",
        value=35,
        index=35,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.TEAMFIGHT_PARTICIPATION, IntervalCalculationAggregationMethod.MAX),
    )
    teamfight_participation__min: CalculationItem = CalculationItem(
        name="teamfight_participation__min",
        description="Team fight participation min",
        value=36,
        index=36,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.TEAMFIGHT_PARTICIPATION, IntervalCalculationAggregationMethod.MIN),
    )
    towers_killed__max: CalculationItem = CalculationItem(
        name="towers_killed__max",
        description="Towers kills",
        value=37,
        index=37,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.TOWERS_KILLED, IntervalCalculationAggregationMethod.MAX),
    )
    towers_killed__gained_pw: CalculationItem = CalculationItem(
        name="towers_killed__gained_pw",
        description="Towers kills gained (per minute)",
        value=38,
        index=38,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.TOWERS_KILLED, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    roshans_killed__max: CalculationItem = CalculationItem(
        name="roshans_killed__max",
        description="Roshan kills",
        value=39,
        index=39,
        postprocessing=PostprocessingItem(carry_comparison=False, support_comparison=False, percentage=False, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.ROSHANS_KILLED, IntervalCalculationAggregationMethod.MAX),
    )
    networth__max: CalculationItem = CalculationItem(
        name="networth__max",
        description="Networth",
        value=40,
        index=40,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.MAX),
        processing=(IntervalCalculationColumn.NETWORTH, IntervalCalculationAggregationMethod.MAX),
    )
    networth__gained_pw: CalculationItem = CalculationItem(
        name="networth__gained_pw",
        description="Networth gained",
        value=41,
        index=41,
        postprocessing=PostprocessingItem(carry_comparison=True, support_comparison=True, percentage=True, total_format=TotalAggregationMethod.AVG),
        processing=(IntervalCalculationColumn.NETWORTH, IntervalCalculationAggregationMethod.GAINED_PW),
    )

    VALUES: list[CalculationItem]
