from typing import Optional, List

from pydantic import condecimal
from sqlmodel import Field, SQLModel, Relationship


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    odota_id: int
    name: str

    cdota_name: Optional[str]

    npc_name: Optional[str]
    npc_name_alias: Optional[str]


# Leagues, Teams and Players
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

    games: Optional["Game"] = Relationship(back_populates="league")


# IN GAME DATA
class InGamePosition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: int
    name: str


class PlayerGameInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    player_id: Optional[int] = Field(default=None, foreign_key="player.id")
    nickname: str

    position_id: Optional[int] = Field(default=None, foreign_key="InGamePosition.id")
    hero_id: Optional[int] = Field(default=None, foreign_key="hero.id")
    lane: int
    is_roaming: bool

    win: bool
    dire: bool

    rank: int
    apm: int
    slot: int
    pings: int

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
    radiant_win: bool

    players_info: List["PlayerGameInfo"] = Relationship(back_populates="game")

    game_start_time: int  # unix timestamp
    duration: int
    replay_url: str


class WindowPlayerComparisonType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Carry => [carry, offlane] / mid to mid / soft support => [hard support, soft support]
    # we compare comparandum to comparans
    comparandum: Optional[int] = Field(default=None, foreign_key="InGamePosition.id")
    comparans: Optional[int] = Field(default=None, foreign_key="InGamePosition.id")


class WindowInfoType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # damage / interval


class WindowInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    comparison_id: Optional[int] = Field(default=None, foreign_key="WindowPlayerComparisonType.id")
    info_type_id: Optional[int] = Field(default=None, foreign_key="WindowInfoType.id")
    description: Optional[str]
    name: str


class WindowPlayer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    slot: int
    player_id: Optional[int] = Field(default=None, foreign_key="player.id")
    hero_id: Optional[int] = Field(default=None, foreign_key="hero.id")


class PlayerPerformanceWindowStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    window_info_id: Optional[int] = Field(default=None, foreign_key="WindowInfo.id")

    player_won: bool
    player_id: Optional[int] = Field(default=None, foreign_key="WindowPlayer.id")
    comparans_id: Optional[int] = Field(default=None, foreign_key="WindowPlayer.id")
    agged_comparison: bool = Field(default=False)

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

    matchdata_id: Optional[int] = Field(default=None, foreign_key="PlayerGameData.id")
    matchdata: Optional["PlayerGameData"] = Relationship(back_populates="stats_window")


class PlayerPerformanceTotalStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

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

    first_blood_claimed: bool = Field(default=False, nullable=False)
    first_kill_time: Optional[int]

    died_first: bool = Field(default=False, nullable=False)
    first_death_time: Optional[int]

    lost_tower_first: bool = Field(default=False, nullable=False)
    lost_tower_lane: Optional[int]
    lost_tower_time: Optional[int]

    destroyed_tower_first: bool = Field(default=False, nullable=False)
    destroyed_tower_lane: Optional[int]
    destroyed_tower_time: Optional[int]

    matchdata_id: Optional[int] = Field(default=None, foreign_key="PlayerGameData.id")
    matchdata: Optional["PlayerGameData"] = Relationship(back_populates="total_stats")


# ADDITIONAL DATA
class RoshanDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]

    stats_id: Optional[int] = Field(default=None, foreign_key="AdditionalMatchStats.id")
    stats: Optional[Team] = Relationship(back_populates="roshan_death")


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

    stats_id: Optional[int] = Field(default=None, foreign_key="AdditionalMatchStats.id")
    stats: Optional[Team] = Relationship(back_populates="hero_death")


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

    building_stats_id: Optional[int] = Field(default=None, foreign_key="BuildingStats.id")
    building_stats: Optional["BuildingStats"] = Relationship(back_populates="buildings_destroyed")


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

    building_stats_id: Optional[int] = Field(default=None, foreign_key="BuildingStats.id")
    building_stats: Optional["BuildingStats"] = Relationship(back_populates="buildings_not_destroyed")


class BuildingStats(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)

    dire: bool

    buildings_destroyed: List["InGameBuildingDestroyed"] = Relationship(back_populates="building_stats")

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

    buildings_not_destroyed_id: Optional[int] = Field(default=None, foreign_key="InGameBuildingNotDestroyed.id")
    buildings_not_destroyed: Optional["InGameBuildingNotDestroyed"] = Relationship(back_populates="building_stats")


# PLAYER FINAL TABLE
class PlayerGameData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key='league.id')
    game_id: Optional[int] = Field(default=None, foreign_key='Game.id')

    player_id: Optional[int] = Field(default=None, foreign_key="player.id")
    player_game_info_id: Optional[int] = Field(default=None, foreign_key="PlayerGameInfo.id")

    additional_stats: Optional[int] = Field(default=None, foreign_key="AdditionalMatchStats.id")
    window_stats: List["PlayerPerformanceWindowStats"] = Relationship(back_populates="matchdata")
    total_stats: List["PlayerPerformanceTotalStats"] = Relationship(back_populates="matchdata")


# GAME AGGREGATION TABLE
class GameAggregatedMock(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)

    window_stats_id: Optional[int] = Field(default=None, foreign_key="PlayerPerformanceWindowStats.id")
    total_stats_id: Optional[int] = Field(default=None, foreign_key="PlayerPerformanceTotalStats.id")

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

    player_agg: List["GameAggregatedByPlayer"] = Relationship(back_populates="matchdata")
    hero_agg: List["GameAggregatedByHero"] = Relationship(back_populates="matchdata")
    position_agg: List["GameAggregatedByPosition"] = Relationship(back_populates="matchdata")


# GAME FINAL TABLE
class GameData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: Optional[int] = Field(default=None, foreign_key='league.id')
    game_id: Optional[int] = Field(default=None, foreign_key='Game.id')

    average_roshan_window_time: Optional[int]
    roshan_death: List["RoshanDeath"] = Relationship(back_populates="roshan_death")

    first_ten_kills_dire: bool
    hero_death: List["HeroDeath"] = Relationship(back_populates="hero_death")

    dire_lost_first_tower: bool
    dire_building_status_id: Optional[int] = Field(default=None, foreign_key="BuildingStats.id")
    sent_building_status_id: Optional[int] = Field(default=None, foreign_key="BuildingStats.id")
