from datetime import datetime
from typing import Optional, List, Dict

import sqlalchemy as db
from pydantic import condecimal
from sqlalchemy.sql import text
from sqlmodel import Field, SQLModel, Relationship, ForeignKey


def _fk(column: str, key_name: str = 'id', bigint: int = False, cascade: bool = False, **column_kwargs) -> Field:
    return Field(sa_column=db.Column(db.BIGINT if bigint else db.Integer,
                                     ForeignKey(f'{column}.{key_name}',
                                                ondelete='CASCADE' if cascade else 'SET NULL', ),
                                     nullable=True,
                                     primary_key=False,
                                     **column_kwargs), )


DEFAULT_SA_KWARGS = {
    "cascade": "all,delete",
    "join_depth": 3,
    "lazy": "selectin"
}


def sa_kwargs_setter(add_default: bool = False, *args, **kwargs) -> Dict[str, str | int]:
    if add_default:
        kwargs = {**DEFAULT_SA_KWARGS, **kwargs, }

    sa_kwargs = dict()
    for arg in args:
        if arg not in DEFAULT_SA_KWARGS:
            raise KeyError
        else:
            sa_kwargs[arg] = DEFAULT_SA_KWARGS[arg]

    for k, v in kwargs.items():
        sa_kwargs[k] = v

    return sa_kwargs



# BASE IN GAME DATA
class Hero(SQLModel, table=True):
    __tablename__ = 'heroes'

    id: int = Field(default=None, primary_key=True)  # open_dota id
    name: str = Field(unique=True, index=True)

    cdota_name: Optional[str]

    npc_name: Optional[str]
    npc_name_alias: Optional[str]


class Position(SQLModel, table=True):
    __tablename__ = 'positions'

    id: int = Field(default=None, primary_key=True, )  # position number
    name: str


class Player(SQLModel, table=True):
    __tablename__ = 'players'

    nickname: str

    account_id: int = Field(default=None, primary_key=True)
    steam_id: Optional[int] = Field(sa_column=db.Column(db.BIGINT, nullable=True, unique=True), )

    official_name: Optional[bool] = Field(default=False)


class Team(SQLModel, table=True):
    __tablename__ = 'teams'

    id: int = Field(default=None, primary_key=True)  # open_dota id
    name: str
    tag: str


class League(SQLModel, table=True):
    __tablename__ = 'leagues'

    id: int = Field(default=None, primary_key=True, index=True)  # steam league id

    pd_link: Optional[str]
    name: Optional[str]
    tier: Optional[int]

    start_date: Optional[int]  # unix time stamp
    end_date: Optional[int]
    has_dates: bool = Field(default=False)

    has_started: Optional[bool] = Field(default=None)
    has_ended: Optional[bool] = Field(default=None)
    fully_parsed: bool = Field(default=False)

    games: List["Game"] = Relationship(back_populates="league", sa_relationship_kwargs=sa_kwargs_setter(False,
                                                                                                        "cascade",
                                                                                                        "lazy",
                                                                                                        order_by="Game.id",
                                                                                                        join_depth=4))


# GAME DATA
class Game(SQLModel, table=True):
    id: int = Field(sa_column=db.Column(db.BIGINT, nullable=False, primary_key=True, index=True), )  # match_id

    name: Optional[str]

    league: Optional[League] = Relationship(back_populates='games')
    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)

    patch = int

    sent_team_id: int = _fk('teams')
    dire_team_id: int = _fk('teams')
    dire_win: bool

    players_data: List["PlayerGameData"] = Relationship(back_populates="game",
                                                        sa_relationship_kwargs=sa_kwargs_setter())

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


class PlayerGameData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    player_id: Optional[int] = Field(default=None, foreign_key="players.account_id")

    position_id: Optional[int] = Field(default=None, foreign_key="positions.id")
    hero_id: Optional[int] = Field(default=None, foreign_key="heroes.id")
    slot: int

    lane: int
    is_roaming: bool

    win: bool
    dire: bool

    rank: Optional[int]
    apm: int
    pings: int

    game_id: Optional[int] = _fk('games', bigint=True, index=True)
    game: Optional["Game"] = Relationship(back_populates="players_data")

    performance: List["GamePerformance"] = Relationship(back_populates="player_game_data",
                                                        sa_relationship_kwargs=sa_kwargs_setter(add_default=True))

    created_at: datetime = Field(sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP"), })

    __tablename__ = 'players_game_data'


# COMPARISON
class ComparisonType(SQLModel, table=True):
    __tablename__ = 'comparison_types'

    id: Optional[int] = Field(default=None, primary_key=True)

    flat: bool  # percent or flat

    basic: Optional[bool] = Field(default=True)  # basic != pos 1 gets compared to pos sum(1, 3) / 2
    player_cpd_id: Optional[int] = _fk('players', 'account_id')
    player_cps_id: Optional[int] = _fk('players', 'account_id')

    hero_cpd_id: Optional[int] = _fk('heroes')
    hero_cps_id: Optional[int] = _fk('heroes')

    pos_cpd_id: Optional[int] = _fk('positions')
    pos_cps_id: Optional[int] = _fk('positions')

    performance: Optional["GamePerformance"] = Relationship(back_populates='comparison')



# AGGREGATION
class DataAggregationType(SQLModel, table=True):
    __tablename__ = 'data_aggregation_types'

    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id")
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP"), })

    by_team_id: Optional[int] = _fk('teams')

    less3: bool
    # additional parameter for aggregation
    by_win: Optional[bool]

    by_player: bool = Field(default=False)
    player_id: Optional[int] = _fk('players', 'account_id')

    by_hero: bool = Field(default=False)
    hero_id: Optional[int] = _fk('heroes')
    by_hero_pos_spec: Optional[int]  # introduced to create new aggregated data if the hero is flexed

    by_position: bool = Field(default=False)
    position_id: Optional[int] = _fk('positions')

    performance: Optional["GamePerformance"] = Relationship(back_populates='aggregation')



# PERFORMANCE DATA
class GamePerformance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    is_comparison: bool = Field(default=False, index=True)
    comparison_id: Optional[int] = Field(default=None, foreign_key="comparison_types.id", index=True)
    comparison: Optional["ComparisonType"] = Relationship(back_populates='performance', )

    is_aggregation: bool = Field(default=False, index=True)
    aggregation_id: Optional[int] = Field(default=None, foreign_key="data_aggregation_types.id", index=True)
    aggregation: Optional["DataAggregationType"] = Relationship(back_populates='performance',
                                                                sa_relationship_kwargs={"cascade": "delete", })

    window_data: List["PerformanceWindowData"] = Relationship(back_populates="game_performance",
                                                              sa_relationship_kwargs=sa_kwargs_setter(add_default=True))
    total_data: List["PerformanceTotalData"] = Relationship(back_populates="game_performance",
                                                            sa_relationship_kwargs=sa_kwargs_setter(add_default=True))

    player_game_data_id: Optional[int] = Field(default=None, foreign_key="players_game_data.id", index=True)
    player_game_data: Optional["PlayerGameData"] = Relationship(back_populates="performance")

    __tablename__ = 'games_performance'


# PERFORMANCE DATA
class PerformanceDataCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # damage / interval

    data_type: List["PerformanceDataType"] = Relationship(back_populates='data_category',
                                                          sa_relationship_kwargs={'lazy': "selectin"}, )

    __tablename__ = 'performance_data_categories'


class PerformanceDataType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    data_category_id: Optional[int] = Field(default=None, foreign_key="performance_data_categories.id", index=True)
    data_category: Optional["PerformanceDataCategory"] = Relationship(back_populates='data_type', )

    pwd: List["PerformanceWindowData"] = Relationship(back_populates='data_type')

    __tablename__ = 'performance_data_types'


# PERFORMANCE DATA INFO
# PERFORMANCE WINDOW
class PerformanceWindowBase(SQLModel):
    l2: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l4: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l6: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l8: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l10: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    ltotal: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)

    g15: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    g30: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    g45: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    g60: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    g60plus: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    gtotal: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)


class PerformanceWindowData(PerformanceWindowBase, table=True):
    __tablename__ = 'performance_windows_data'

    id: Optional[int] = Field(default=None, primary_key=True)

    data_type_id: Optional[int] = Field(default=None, foreign_key="performance_data_types.id")
    data_type: Optional["PerformanceDataType"] = Relationship(back_populates='pwd')

    game_performance_id: Optional[int] = Field(default=None, foreign_key="games_performance.id")
    game_performance: Optional["GamePerformance"] = Relationship(back_populates='window_data',
                                                                 sa_relationship_kwargs=sa_kwargs_setter(add_default=True,
                                                                                                         join_depth=0))


# PERFORMANCE TOTAL
class PerformanceTotalBase(SQLModel):

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

    first_blood_claimed: condecimal(max_digits=5, decimal_places=2) = Field(default=None, nullable=True)
    first_kill_time: Optional[int]

    died_first: condecimal(max_digits=5, decimal_places=2) = Field(default=None, nullable=True)
    first_death_time: Optional[int]

    lost_tower_first: condecimal(max_digits=5, decimal_places=2) = Field(default=None, nullable=True)
    lost_tower_lane: Optional[int]
    lost_tower_time: Optional[int]

    destroyed_tower_first: condecimal(max_digits=5, decimal_places=2) = Field(default=None, nullable=True)
    destroyed_tower_lane: Optional[int]
    destroyed_tower_time: Optional[int]


class PerformanceTotalData(PerformanceTotalBase, table=True):
    __tablename__ = 'performance_totals_data'
    id: Optional[int] = Field(default=None, primary_key=True)

    game_performance_id: Optional[int] = Field(default=None, foreign_key="games_performance.id")
    game_performance: Optional["GamePerformance"] = Relationship(back_populates='total_data',
                                                                 sa_relationship_kwargs=sa_kwargs_setter(add_default=True,
                                                                                                         join_depth=0))


# ADDITIONAL DATA
class RoshanDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]

    game_id: Optional[int] = _fk('games', bigint=True)
    game: Optional["Game"] = Relationship(back_populates='roshan_death')

    __tablename__ = 'roshan_deaths'


class HeroDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]
    killer_hero_id: Optional[int] = _fk('heroes')
    killer_player_id: Optional[int] = _fk('players', 'account_id')

    victim_dire: Optional[bool]
    victim_hero_id: Optional[int] = _fk('heroes')
    victim_player_id: Optional[int] = _fk('players', 'account_id')

    game_id: Optional[int] = _fk('games', bigint=True)
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


# VIEW DATA
class PerformanceViewBase(SQLModel):
    __table_args__ = {'info': {
        'is_view': True
    }}

    match_id: int = Field(sa_column=db.Column(db.BIGINT, nullable=False, primary_key=True), )  # match_id
    league_id: Optional[int] = Field(default=None)
    dire_win: bool
    average_roshan_window_time: Optional[int]
    first_ten_kills_dire: bool
    dire_lost_first_tower: bool

    team_id: Optional[int] = Field(default=None)
    player_id: Optional[int] = Field(default=None)
    position_id: Optional[int] = Field(default=None)
    hero_id: Optional[int] = Field(default=None)
    slot: int
    lane: int
    is_roaming: bool
    win: bool
    dire: bool
    rank: Optional[int]
    apm: int
    pings: int

    is_comparison: bool = Field(default=False)
    comparison_id: Optional[int] = Field(default=None)
    is_aggregation: bool = Field(default=False)
    aggregation_id: Optional[int] = Field(default=None)

    flat: bool  # percent or flat
    basic: bool = Field(default=True)  # general = pos 1 gets compared to pos sum(1, 3) / 2
    player_cpd_id: Optional[int] = Field(default=True)
    player_cps_id: Optional[int] = Field(default=True)
    hero_cpd_id: Optional[int] = Field(default=True)
    hero_cps_id: Optional[int] = Field(default=True)
    pos_cpd_id: Optional[int] = Field(default=True)
    pos_cps_id: Optional[int] = Field(default=True)

    agg_less3: bool
    agg_league_id: Optional[int] = Field(default=True)
    agg_by_win: Optional[bool]
    agg_by_player: bool = Field(default=False)
    agg_player_id: Optional[int] = Field(default=True)
    agg_by_hero: bool = Field(default=False)
    agg_hero_id: Optional[int] = Field(default=True)
    agg_by_hero_pos_spec: Optional[int]  # introduced to create new aggregated data if the hero is flexed
    agg_by_position: bool = Field(default=False)
    agg_position_id: Optional[int] = Field(default=True)


class PerformanceTotalView(PerformanceViewBase, PerformanceTotalBase, table=True):
    __tablename__ = 'performance_total_view'


class PerformanceWindowView(PerformanceViewBase, PerformanceWindowBase, table=True):
    __tablename__ = 'performance_window_view'

    data_type_id: Optional[int]
