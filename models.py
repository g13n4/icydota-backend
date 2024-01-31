from typing import Optional, List

import sqlalchemy as db
from pydantic import condecimal
from sqlmodel import Field, SQLModel, Relationship, ForeignKey


def _fk(column_name: str, **column_kwargs) -> Field:
    return Field(sa_column=db.Column(db.Integer,
                                     ForeignKey(f'{column_name}.id',
                                                ondelete='SET NULL', ),
                                     nullable=True,
                                     primary_key=False,
                                     **column_kwargs), )


# BASE IN GAME DATA
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    odota_id: int = Field(unique=True, index=True)
    name: str = Field(unique=True, index=True)

    cdota_name: Optional[str]

    npc_name: Optional[str]
    npc_name_alias: Optional[str]

    __tablename__ = 'heroes'


class Position(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: int = Field(unique=True)
    name: str

    __tablename__ = 'positions'


class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: str

    account_id: Optional[int] = Field(unique=True, index=True)
    steam_id: Optional[int] = Field(sa_column=db.Column(db.BIGINT, nullable=True, unique=True), )

    official_name: Optional[bool] = Field(default=False)

    __tablename__ = 'players'


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    odota_id: int = Field(unique=True, index=True)
    name: str
    tag: str

    __tablename__ = 'teams'


class League(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    pd_link: Optional[str]
    league_id: int = Field(unique=True, index=True)
    name: Optional[str]
    tier: Optional[int]

    start_date: Optional[int]  # unix time stamp
    end_date: Optional[int]
    has_dates: bool = Field(default=False)

    has_started: Optional[bool] = Field(default=None)
    has_ended: Optional[bool] = Field(default=None)
    fully_parsed: bool = Field(default=False)

    games: List["Game"] = Relationship(back_populates="league")

    __tablename__ = 'leagues'




# GAME DATA
class PlayerGameData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    player_id: Optional[int] = Field(default=None, foreign_key="players.id")

    position_id: Optional[int] = Field(default=None, foreign_key="positions.id")
    hero_id: Optional[int] = Field(default=None, foreign_key="heroes.id")
    slot: int

    lane: int
    is_roaming: bool

    win: bool
    dire: bool

    rank: int
    apm: int
    pings: int

    performance: Optional["GamePerformance"] = Relationship(back_populates="player_game_data")
    performance_id: Optional[int] = Field(default=None, foreign_key="games_performance.id")

    game: Optional["Game"] = Relationship(back_populates="players_data")
    game_id: Optional[int] = Field(default=None, foreign_key="games.id")

    __tablename__ = 'player_games_data'


class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    match_id: int = Field(sa_column=db.Column(db.BIGINT, nullable=False, unique=True), )

    league: Optional[League] = Relationship(back_populates='games')
    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id")

    patch = int

    sent_team_id: int = _fk('teams')
    dire_team_id: int = _fk('teams')
    dire_win: bool

    players_data: List["PlayerGameData"] = Relationship(back_populates="game")

    average_roshan_window_time: Optional[int]
    roshan_death: List["RoshanDeath"] = Relationship(back_populates="game")

    first_ten_kills_dire: bool
    hero_death: List["HeroDeath"] = Relationship(back_populates="game")

    dire_lost_first_tower: bool
    dire_building_status_id: Optional[int] = Field(default=None, foreign_key="buildings_data.id")
    sent_building_status_id: Optional[int] = Field(default=None, foreign_key="buildings_data.id")

    game_start_time: int = Field(sa_column=db.Column(db.BIGINT, nullable=False, unique=False), )  # unix timestamp
    duration: int
    replay_url: str

    __tablename__ = 'games'


# COMPARISON
class ComparisonType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # cpd - comparandum / cps - comparans

    percent: bool  # percent or flat

    player_cpd_id: Optional[int] = _fk('players')
    player_cps_id: Optional[int] = _fk('players')

    hero_cpd_id: Optional[int] = _fk('heroes')
    hero_cps_id: Optional[int] = _fk('heroes')

    pos_cpd_id: Optional[int] = _fk('positions')
    pos_cps_id: Optional[int] = _fk('positions')

    data_description: Optional["PerformanceDataDescription"] = Relationship(back_populates='comparison')

    __tablename__ = 'comparison_types'


# AGGREGATION
class DataAggregationType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    by_player: bool = Field(default=False)
    player_id: Optional[int] = _fk('players')

    by_hero: bool = Field(default=False)
    hero_id: Optional[int] = _fk('heroes')

    by_position: bool = Field(default=False)
    position_id: Optional[int] = _fk('positions')

    data_description: Optional["PerformanceDataDescription"] = Relationship(back_populates='aggregation')

    __tablename__ = 'data_aggregation_types'


# PERFORMANCE DATA
class GamePerformance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    window_data: List["PerformanceWindowData"] = Relationship(back_populates="game_performance")
    total_data: List["PerformanceTotalData"] = Relationship(back_populates="game_performance")

    player_game_data: Optional["PlayerGameData"] = Relationship(back_populates="performance")

    __tablename__ = 'games_performance'


class PerformanceDataCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # damage / interval

    data_type: List["PerformanceDataType"] = Relationship(back_populates='data_category')

    __tablename__ = 'performance_data_categories'


class PerformanceDataType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    data_category_id: Optional[int] = Field(default=None, foreign_key="performance_data_categories.id")
    data_category: Optional["PerformanceDataCategory"] = Relationship(back_populates='data_type')

    __tablename__ = 'performance_data_types'


class PerformanceDataDescription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    data_type_id: Optional[int] = Field(default=None, foreign_key="performance_data_types.id")
    is_total_stats: bool = Field(default=False)

    name: Optional[str]  # generate

    is_comparison: bool = Field(default=False)
    comparison_id: Optional[int] = Field(default=None, foreign_key="comparison_types.id")
    comparison: Optional["ComparisonType"] = Relationship(back_populates='data_description')

    is_aggregation: bool = Field(default=False)
    aggregation_id: Optional[int] = Field(default=None, foreign_key="data_aggregation_types.id")
    aggregation: Optional["DataAggregationType"] = Relationship(back_populates='data_description')

    pwd: Optional["PerformanceWindowData"] = Relationship(back_populates='data_info')
    ptd: Optional["PerformanceTotalData"] = Relationship(back_populates='data_info')

    __tablename__ = 'performance_data_descriptions'


# PERFORMANCE DATA INFO
class PerformanceWindowData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    data_info_id: Optional[int] = Field(default=None, foreign_key="performance_data_descriptions.id")
    data_info: Optional["PerformanceDataDescription"] = Relationship(back_populates='pwd')

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

    game_performance_id: Optional[int] = Field(default=None, foreign_key="games_performance.id")
    game_performance: Optional["GamePerformance"] = Relationship(back_populates='window_data')

    __tablename__ = 'performance_windows_data'


class PerformanceTotalData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    data_info_id: Optional[int] = Field(default=None, foreign_key="performance_data_descriptions.id")
    data_info: Optional["PerformanceDataDescription"] = Relationship(back_populates='ptd')

    total_gold: int
    total_xp: int
    kills_per_min: condecimal(max_digits=10, decimal_places=2) = Field(nullable=False)
    kda: condecimal(max_digits=5, decimal_places=2) = Field(nullable=False)

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

    game_performance_id: Optional[int] = Field(default=None, foreign_key="games_performance.id")
    game_performance: Optional["GamePerformance"] = Relationship(back_populates='total_data')

    __tablename__ = 'performance_totals_data'


# ADDITIONAL DATA
class RoshanDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]

    game_id: Optional[int] = Field(default=None, foreign_key="games.id")
    game: Optional["Game"] = Relationship(back_populates='roshan_death')

    __tablename__ = 'roshan_deaths'


class HeroDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]
    killer_hero_id: Optional[int] = _fk('heroes')
    killer_player_id: Optional[int] = _fk('players')

    victim_dire: Optional[bool]
    victim_hero_id: Optional[int] = _fk('heroes')
    victim_player_id: Optional[int] = _fk('players')

    game_id: Optional[int] = Field(default=None, foreign_key="games.id")
    game: Optional["Game"] = Relationship(back_populates='hero_death')

    __tablename__ = 'hero_deaths'


# BUILDINGS
class InGameBuilding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str

    lane: int

    is_tower: bool  # or rax
    tier: Optional[int]
    tower4: Optional[bool]  # False - first, True - second one

    is_rax: Optional[bool]
    melee: Optional[bool]

    __tablename__ = 'in_game_buildings'


class InGameBuildingDestroyed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    building_id: Optional[int] = _fk("in_game_buildings")
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

    building_data_id: Optional[int] = Field(default=None, foreign_key="buildings_data.id")
    building_data: Optional["BuildingData"] = Relationship(back_populates="destruction_order")

    __tablename__ = 'in_game_buildings_destroyed'


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

    building_data: Optional["BuildingData"] = Relationship(back_populates="not_destroyed")

    __tablename__ = 'in_game_buildings_not_destroyed'


class BuildingData(SQLModel, table=True):
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

    not_destroyed: Optional["InGameBuildingNotDestroyed"] = Relationship(back_populates="building_data")
    not_destroyed_id: Optional[int] = Field(default=None, foreign_key="in_game_buildings_not_destroyed.id")

    __tablename__ = 'buildings_data'


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

    window_stats_id: Optional[int] = Field(default=None, foreign_key="games_performance.id")

    game_aggregated_data_id: Optional[int] = Field(default=None, foreign_key="games_aggregated_data.id")


class GameAggregatedByPlayer(GameAggregatedMock, table=True):
    player_id: Optional[int] = Field(default=None, foreign_key="players.id")
    game_agg_data: Optional["GameAggregatedData"] = Relationship(back_populates="player_agg")

    __tablename__ = 'games_aggregated_by_player'


class GameAggregatedByHero(GameAggregatedMock, table=True):
    hero_id: Optional[int] = Field(default=None, foreign_key="heroes.id")
    game_agg_data: Optional["GameAggregatedData"] = Relationship(back_populates="hero_agg")

    __tablename__ = 'games_aggregated_by_hero'


class GameAggregatedByPosition(GameAggregatedMock, table=True):
    position_id: Optional[int] = Field(default=None, foreign_key="positions.id")
    game_agg_data: Optional["GameAggregatedData"] = Relationship(back_populates="position_agg", )

    __tablename__ = 'games_aggregated_by_position'


class GameAggregatedData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id")

    player_agg: List["GameAggregatedByPlayer"] = Relationship(back_populates="game_agg_data")
    hero_agg: List["GameAggregatedByHero"] = Relationship(back_populates="game_agg_data")
    position_agg: List["GameAggregatedByPosition"] = Relationship(back_populates="game_agg_data")

    __tablename__ = 'games_aggregated_data'
