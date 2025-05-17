from enum import StrEnum, auto, Enum

from constants.calculation.game.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.game.calculation_type.helpers import CalculationItem, set_category_and_value, \
    PostprocessingItem, add_values
from constants.calculation.game.category import WindowCategories


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
    MOVEMENT_UNIQUE = auto()



class IntervalCalculationAggregationMethod(Enum):
    MIN = 1
    AVG = 2
    MAX = 3
    SUM = 4

    GAINED_PW = 5

    GAINED_PM_MEDIAN = 6
    MAX_GLOBAL_PERC = 7
    AVG_BY_LENGTH_PM = 8

    COEFF = 9
    CONVERT = 10


@add_values
@set_category_and_value(WindowCategories.INTERVAL)
class IntervalCalculations:
    gold__max: CalculationItem = CalculationItem(
        name="gold__max",
        description="Gold",
        index=1,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.MAX),
    )
    gold__gained_pm_median: CalculationItem = CalculationItem(
        name="gold__gained_pm_median",
        description="Gold median (per minute)",
        index=2,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.GAINED_PM_MEDIAN),
    )
    gold__gained_pw: CalculationItem = CalculationItem(
        name="gold__gained_pw",
        description="Gold gained",
        index=3,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    gold__avg_by_length_pm: CalculationItem = CalculationItem(
        name="gold__avg_by_length_pm",
        description="GPM",
        index=4,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    gold__max_global_perc: CalculationItem = CalculationItem(
        name="gold__max_global_perc",
        description="Gold control (total%)",
        index=5,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.GOLD, IntervalCalculationAggregationMethod.MAX_GLOBAL_PERC),
    )
    xp__max: CalculationItem = CalculationItem(
        name="xp__max",
        description="XP",
        index=6,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.MAX),
    )
    xp__gained_pm_median: CalculationItem = CalculationItem(
        name="xp__gained_pm_median",
        description="XP median (per minute)",
        index=7,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.GAINED_PM_MEDIAN),
    )
    xp__gained_pw: CalculationItem = CalculationItem(
        name="xp__gained_pw",
        description="XP gained",
        index=8,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    xp__avg_by_length_pm: CalculationItem = CalculationItem(
        name="xp__avg_by_length_pm",
        description="XPM",
        index=9,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    xp__max_global_perc: CalculationItem = CalculationItem(
        name="xp__max_global_perc",
        description="XP control (total%)",
        index=10,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.MAX_GLOBAL_PERC),
    )
    lh__max: CalculationItem = CalculationItem(
        name="lh__max",
        description="Last hits",
        index=11,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.LH, IntervalCalculationAggregationMethod.MAX),
    )
    lh__gained_pw: CalculationItem = CalculationItem(
        name="lh__gained_pw",
        description="Last hits gained",
        index=12,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.LH, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    lh__avg_by_length_pm: CalculationItem = CalculationItem(
        name="lh__avg_by_length_pm",
        description="Last hits average (per minute)",
        index=13,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.LH, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    movement__sum: CalculationItem = CalculationItem(
        name="movement__sum",
        description="Distance traveled",
        index=14,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
        ),
        processing=(IntervalCalculationColumn.MOVEMENT, IntervalCalculationAggregationMethod.SUM),
    )
    movement__avg_by_length_pm: CalculationItem = CalculationItem(
        name="movement__avg_by_length_pm",
        description="Distance traveled (per minute)",
        index=15,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.MOVEMENT, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    level__max: CalculationItem = CalculationItem(
        name="level__max",
        description="Level",
        index=16,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.LEVEL, IntervalCalculationAggregationMethod.MAX),
    )
    level__gained_pw: CalculationItem = CalculationItem(
        name="level__gained_pw",
        description="Levels gained",
        index=17,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.LEVEL, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    kills__max: CalculationItem = CalculationItem(
        name="kills__max",
        description="Kills",
        index=18,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.KILLS, IntervalCalculationAggregationMethod.MAX),
    )
    kills__avg_by_length_pm: CalculationItem = CalculationItem(
        name="kills__avg_by_length_pm",
        description="Kills average (per minute)",
        index=19,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.KILLS, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    kills__max_global_perc: CalculationItem = CalculationItem(
        name="kills__max_global_perc",
        description="Kills control (total%)",
        index=20,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.KILLS, IntervalCalculationAggregationMethod.MAX_GLOBAL_PERC),
    )
    deaths__max: CalculationItem = CalculationItem(
        name="deaths__max",
        description="Deaths",
        index=21,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.DEATHS, IntervalCalculationAggregationMethod.MAX),
    )
    deaths__avg_by_length_pm: CalculationItem = CalculationItem(
        name="deaths__avg_by_length_pm",
        description="Deaths average (per minute)",
        index=22,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.DEATHS, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    deaths__max_global_perc: CalculationItem = CalculationItem(
        name="deaths__max_global_perc",
        description="Deaths control (total%)",
        index=23,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.DEATHS, IntervalCalculationAggregationMethod.MAX_GLOBAL_PERC),
    )
    kda__max: CalculationItem = CalculationItem(
        name="kda__max",
        description="KDA",
        index=24,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.KDA, IntervalCalculationAggregationMethod.MAX),
    )
    kda__avg_by_length_pm: CalculationItem = CalculationItem(
        name="kda__avg_by_length_pm",
        description="KDA average (per minute)",
        index=25,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.KDA, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    kda__gained_pw: CalculationItem = CalculationItem(
        name="kda__gained_pw",
        description="KDA gained",
        index=26,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.KDA, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    obs_placed__max: CalculationItem = CalculationItem(
        name="obs_placed__max",
        description="Observer wards placed",
        index=27,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.OBS_PLACED, IntervalCalculationAggregationMethod.MAX),
    )
    obs_placed__avg_by_length_pm: CalculationItem = CalculationItem(
        name="obs_placed__avg_by_length_pm",
        description="Observer wards placed (per minute)",
        index=28,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.OBS_PLACED, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    sen_placed__max: CalculationItem = CalculationItem(
        name="sen_placed__max",
        description="Sentry wards placed",
        index=29,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.SEN_PLACED, IntervalCalculationAggregationMethod.MAX),
    )
    sen_placed__avg_by_length_pm: CalculationItem = CalculationItem(
        name="sen_placed__avg_by_length_pm",
        description="Sentry wards placed (per minute)",
        index=30,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.SEN_PLACED, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    stacked__max: CalculationItem = CalculationItem(
        name="stacked__max",
        description="Stacked",
        index=31,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.STACKED, IntervalCalculationAggregationMethod.MAX),
    )
    stacked__avg_by_length_pm: CalculationItem = CalculationItem(
        name="stacked__avg_by_length_pm",
        description="Stacked average (per minute)",
        index=32,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.STACKED, IntervalCalculationAggregationMethod.AVG_BY_LENGTH_PM),
    )
    rune_pickups__max: CalculationItem = CalculationItem(
        name="rune_pickups__max",
        description="Runes picked up",
        index=33,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
        ),
        processing=(IntervalCalculationColumn.RUNE_PICKUPS, IntervalCalculationAggregationMethod.MAX),
    )
    teamfight_participation__avg: CalculationItem = CalculationItem(
        name="teamfight_participation__avg",
        description="Team fight participation average",
        index=34,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.TEAMFIGHT_PARTICIPATION, IntervalCalculationAggregationMethod.AVG),
    )
    teamfight_participation__max: CalculationItem = CalculationItem(
        name="teamfight_participation__max",
        description="Team fight participation max",
        index=35,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.TEAMFIGHT_PARTICIPATION, IntervalCalculationAggregationMethod.MAX),
    )
    teamfight_participation__min: CalculationItem = CalculationItem(
        name="teamfight_participation__min",
        description="Team fight participation min",
        index=36,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.TEAMFIGHT_PARTICIPATION, IntervalCalculationAggregationMethod.MIN),
    )
    towers_killed__max: CalculationItem = CalculationItem(
        name="towers_killed__max",
        description="Towers kills",
        index=37,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.TOWERS_KILLED, IntervalCalculationAggregationMethod.MAX),
    )
    towers_killed__gained_pw: CalculationItem = CalculationItem(
        name="towers_killed__gained_pw",
        description="Towers kills gained (per minute)",
        index=38,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.TOWERS_KILLED, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    roshans_killed__max: CalculationItem = CalculationItem(
        name="roshans_killed__max",
        description="Roshan kills",
        index=39,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.ROSHANS_KILLED, IntervalCalculationAggregationMethod.MAX),
    )
    networth__max: CalculationItem = CalculationItem(
        name="networth__max",
        description="Networth",
        index=40,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX
        ),
        processing=(IntervalCalculationColumn.NETWORTH, IntervalCalculationAggregationMethod.MAX),
    )
    networth__gained_pw: CalculationItem = CalculationItem(
        name="networth__gained_pw",
        description="Networth gained",
        index=41,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.AVG
        ),
        processing=(IntervalCalculationColumn.NETWORTH, IntervalCalculationAggregationMethod.GAINED_PW),
    )
    movement__unique__tiles__sum: CalculationItem = CalculationItem(
        name="movement__unique__tiles__sum",
        description="Distance traveled (unique tiles only)",
        index=42,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM
        ),
        processing=(IntervalCalculationColumn.MOVEMENT_UNIQUE, IntervalCalculationAggregationMethod.SUM),
    )
    movement__unique__coeff: CalculationItem = CalculationItem(
        name="movement__coefficient",
        description="Unique travel distance coefficient",
        index=43,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.SUM,
            calculated_later=True,
        ),
        processing=(IntervalCalculationColumn.MOVEMENT_UNIQUE, IntervalCalculationAggregationMethod.COEFF),
    )
    xp__lvl: CalculationItem = CalculationItem(
        name="xp__lvl",
        description="XP (LVL)",
        index=44,
        postprocessing=PostprocessingItem(
            total_format=TotalAggregationMethod.MAX,
            calculated_later=True,
        ),
        processing=(IntervalCalculationColumn.XP, IntervalCalculationAggregationMethod.CONVERT),
    )

    VALUES: list[CalculationItem]
    VALUES_NAMES: list[str]
