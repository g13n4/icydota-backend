from typing import Optional, List

from pydantic import condecimal
from sqlmodel import Field, SQLModel, Relationship


# BASE IN GAME DATA
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    odota_id: int
    name: str

    cdota_name: Optional[str]

    npc_name: Optional[str]
    npc_name_alias: Optional[str]


class Position(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: int
    name: str


class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: str
    steam_id: int


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    odota_id: int
    name: str
    tag: str


class League(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pd_link: str
    league_id: int
    name: Optional[str]
    tier: int

    start_date: Optional[int]  # unix time stamp
    end_date: Optional[int]

    ended: bool
    fully_parsed: bool

    games: List["Game"] = Relationship(back_populates="league")


# GAME DATA
class PlayerGameData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    player_id: Optional[int] = Field(default=None, foreign_key="player.id")

    nickname: str

    position_id: Optional[int] = Field(default=None, foreign_key="Position.id")
    hero_id: Optional[int] = Field(default=None, foreign_key="hero.id")
    slot: int

    lane: int
    is_roaming: bool

    win: bool
    dire: bool

    rank: int
    apm: int
    pings: int

    performance: Optional["GamePerformance"] = Relationship(back_populates="player_game_data")
    performance_id: Optional[int] = Field(default=None, foreign_key="GamePerformance.id")

    game: Optional["Game"] = Relationship(back_populates="players_info")
    game_id: Optional[int] = Field(default=None, foreign_key="game.id")


class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    match_id: int

    league: Optional[League] = Relationship(back_populates='games')
    league_id: Optional[int] = Field(default=None, foreign_key='league.id')

    patch = int

    radiant_team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    dire_team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    dire_win: bool

    players_data: List["PlayerGameData"] = Relationship(back_populates="game")

    average_roshan_window_time: Optional[int]
    roshan_death: List["RoshanDeath"] = Relationship(back_populates="roshan_death")

    first_ten_kills_dire: bool
    hero_death: List["HeroDeath"] = Relationship(back_populates="hero_death")

    dire_lost_first_tower: bool
    dire_building_status_id: Optional[int] = Field(default=None, foreign_key="BuildingData.id")
    sent_building_status_id: Optional[int] = Field(default=None, foreign_key="BuildingData.id")

    game_start_time: int  # unix timestamp
    duration: int
    replay_url: str


# PERFORMANCE DATA
class GamePerformance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    window_data: List["PerformanceWindowData"] = Relationship(back_populates="game_performance")
    total_data: List["PerformanceTotalData"] = Relationship(back_populates="game_performance")

    player_game_data: Optional["PlayerGameData"] = Relationship(back_populates="player_performance")
    player_game_data_id: Optional[int] = Field(default=None, foreign_key="PlayerGameData.id")


# COMPARISON
class ComparisonType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # cpd - comparandum / cps - comparans

    player_cpd_id: Optional[int] = Field(default=None, foreign_key="Player.id")
    player_cps_id: Optional[int] = Field(default=None, foreign_key="Player.id")

    hero_cpd_id: Optional[int] = Field(default=None, foreign_key="Hero.id")
    hero_cps_id: Optional[int] = Field(default=None, foreign_key="Hero.id")

    pos_cpd_id: Optional[int] = Field(default=None, foreign_key="Position.id")
    pos_cps_id: Optional[int] = Field(default=None, foreign_key="Position.id")

    data_info: Optional["PerformanceDataDescription"] = Relationship(back_populates="comparison_type")


# AGGREGATION
class DataAggregationType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    by_player: bool = Field(default=False)
    player_id: Optional[int] = Field(default=None, foreign_key="Hero.id")

    by_hero: bool = Field(default=False)
    hero_id: Optional[int] = Field(default=None, foreign_key="Hero.id")

    by_position: bool = Field(default=False)
    position_id: Optional[int] = Field(default=None, foreign_key="Position.id")

    data_info_id: Optional[int] = Field(default=None, foreign_key="DataAggregationType.id")
    data_info: Optional["PerformanceDataDescription"] = Relationship(back_populates='aggregation')


# PERFORMANCE DATA INFO
class PerformanceDataCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # damage / interval

    data_type: List["PerformanceDataType"] = Relationship(back_populates='data_category')


class PerformanceDataType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Number of dewarded observers

    data_category_id: Optional[int] = Field(default=None, foreign_key="PerformanceDataCategory.id")
    data_category: Optional["PerformanceDataCategory"] = Relationship(back_populates='data_type')


class PerformanceDataDescription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    data_type_id: Optional[int] = Field(default=None, foreign_key="PerformanceDataType.id")
    is_total_stats: bool = Field(default=False)

    name: Optional[str]  # generate

    is_comparison: bool = Field(default=False)
    comparison_id: Optional[int] = Field(default=None, foreign_key="ComparisonType.id")
    comparison: Optional["ComparisonType"] = Relationship(back_populates='player_stats_info')

    is_aggregation: bool = Field(default=False)
    aggregation_id: Optional[int] = Field(default=None, foreign_key="DataAggregationType.id")
    aggregation: Optional["DataAggregationType"] = Relationship(back_populates='data_info')

    performance_window_data_id: Optional[int] = Field(default=None, foreign_key="PerformanceWindowData.id")
    performance_window_data: Optional["PerformanceWindowData"] = Relationship(back_populates='data_info')

    performance_total_data_id: Optional[int] = Field(default=None, foreign_key="PerformanceTotalData.id")
    performance_total_data: Optional["PerformanceTotalData"] = Relationship(back_populates='data_info')


# PERFORMANCE DATA INFO
class PerformanceWindowData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    data_info_id: Optional[int] = Field(default=None, foreign_key="PerformanceDataDescription.id")
    data_info: Optional[PerformanceDataDescription] = Relationship(back_populates='performance_window_stats')

    # laning
    l2: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l4: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l6: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l8: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l10: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    ltotal: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)

    # next phase
    g15: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    g30: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    g45: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    g60: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    g60plus: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    gtotal: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)

    game_performance_id: Optional[int] = Field(default=None, foreign_key="GamePerformance.id")
    game_performance: Optional["GamePerformance"] = Relationship(back_populates='window_data')


class PerformanceTotalData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    data_info_id: Optional[int] = Field(default=None, foreign_key="PerformanceDataDescription.id")
    data_info: Optional[PerformanceDataDescription] = Relationship(back_populates='performance_total_stats')

    total_gold: int
    total_xp: int
    kills_per_min: int
    kda: int

    neutral_kills: int
    tower_kills: int
    courier_kills: int

    lane_kills: int
    hero_kills: int
    observer_kills: int
    sentry_kills: int
    roshan_kills: int
    runes_picked_up: int

    ancient_kills: int
    buyback_count: int
    observer_uses: int
    sentry_uses: int

    lane_efficiency: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    lane_efficiency_pct: int

    first_blood_claimed: bool = Field(default=False, nullable=True)
    first_kill_time: Optional[int]

    died_first: bool = Field(default=False, nullable=True)
    first_death_time: Optional[int]

    lost_tower_first: bool = Field(default=False, nullable=True)
    lost_tower_lane: Optional[int]
    lost_tower_time: Optional[int]

    destroyed_tower_first: bool = Field(default=False, nullable=True)
    destroyed_tower_lane: Optional[int]
    destroyed_tower_time: Optional[int]

    game_performance_id: Optional[int] = Field(default=None, foreign_key="GamePerformance.id")
    game_performance: Optional["GamePerformance"] = Relationship(back_populates='total_data')



# ADDITIONAL DATA
class RoshanDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]


class HeroDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]
    killer_hero_id: Optional[int] = Field(default=None, foreign_key="hero.id")
    killer_player_id: Optional[int] = Field(default=None, foreign_key="player.id")

    victim_dire: Optional[bool]
    victim_hero_id: Optional[int] = Field(default=None, foreign_key="hero.id")
    victim_player_id: Optional[int] = Field(default=None, foreign_key="player.id")


# BUILDINGS
class InGameBuilding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str

    lane: int

    is_tower: bool  # or rax
    tier: Optional[int]
    tower4: Optional[bool]  # False - first, True - second one

    is_rax: bool
    melee: bool


class InGameBuildingDestroyed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    building_id: Optional[int] = Field(default=None, foreign_key='ingamebuilding.id')
    death_time: int

    destruction_order: Optional[int]
    destruction_order_tower: Optional[int]
    destruction_order_rax: Optional[int]

    # additional rax info
    destroyed_lane_1: bool = Field(default=False)
    destroyed_lane_2: bool = Field(default=False)
    destroyed_lane_3: bool = Field(default=False)

    megacreeps: bool = Field(default=False)

    # additional tower info
    naked_throne: bool = Field(default=False)

    building_data_id: Optional[int] = Field(default=None, foreign_key="BuildingData.id")
    building_data: Optional["BuildingData"] = Relationship(back_populates="destruction_order")


class InGameBuildingNotDestroyed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    towers_left_top: int
    towers_left_mid: int
    towers_left_bottom: int
    towers_left_throne: int

    towers_left_total: int

    rax_left_top: int
    rax_left_mid: int
    rax_left_bottom: int

    rax_left_total: int

    building_data_id: Optional[int] = Field(default=None, foreign_key="BuildingData.id")
    building_data: Optional["BuildingData"] = Relationship(back_populates="not_destroyed")


class BuildingData(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)

    dire: bool

    destruction_order: List["InGameBuildingDestroyed"] = Relationship(back_populates="building_data")

    destroyed_buildings: Optional[int]
    destroyed_towers: Optional[int]
    destroyed_rax: Optional[int]

    # additional rax info
    destroyed_lane_1: bool = Field(default=False)
    destroyed_lane_2: bool = Field(default=False)
    destroyed_lane_3: bool = Field(default=False)

    megacreeps: Optional[bool]

    # additional tower info
    naked_throne: Optional[bool]

    not_destroyed_id: Optional[int] = Field(default=None, foreign_key="InGameBuildingNotDestroyed.id")
    not_destroyed: Optional["InGameBuildingNotDestroyed"] = Relationship(back_populates="building_data")


# TODO: make a player game data like view
#
# class PlayerGameData(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#
#     league_id: Optional[int] = Field(default=None, foreign_key='league.id')
#     game_id: Optional[int] = Field(default=None, foreign_key='Game.id')
#     team_id: Optional[int] = Field(default=None, foreign_key='Team.id')
#     player_id: Optional[int] = Field(default=None, foreign_key="player.id")
#     position_id: Optional[int] = Field(default=None, foreign_key="player.id")
#     win: bool
#
#     player_performance_id: Optional[int] = Field(default=None, foreign_key="GamePerformance.id")


# AGGREGATION
class GameAggregatedMock(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)

    window_stats_id: Optional[int] = Field(default=None, foreign_key="GamePerformance.id")

    game_aggregated_data_id: Optional[int] = Field(default=None, foreign_key="GameAggregatedData.id")


class GameAggregatedByPlayer(GameAggregatedMock, table=True):
    player_id: Optional[int] = Field(default=None, foreign_key="player.id")
    game_agg_data: Optional["GameAggregatedData"] = Relationship(back_populates="player_agg")


class GameAggregatedByHero(GameAggregatedMock, table=True):
    hero_id: Optional[int] = Field(default=None, foreign_key="hero.id")
    game_agg_data: Optional["GameAggregatedData"] = Relationship(back_populates="hero_agg")


class GameAggregatedByPosition(GameAggregatedMock, table=True):
    position_id: Optional[int] = Field(default=None, foreign_key="InGamePosition.id")
    game_agg_data: Optional["GameAggregatedData"] = Relationship(back_populates="position_agg")


class GameAggregatedData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key='league.id')

    player_agg: List["GameAggregatedByPlayer"] = Relationship(back_populates="game_agg_data")
    hero_agg: List["GameAggregatedByHero"] = Relationship(back_populates="game_agg_data")
    position_agg: List["GameAggregatedByPosition"] = Relationship(back_populates="game_agg_data")
