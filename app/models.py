from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import condecimal
import datetime


# Items and Heroes
class InGameEntityBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    odota_id: int
    ingame_name: str
    name: str


class Hero(InGameEntityBase, table=True):
    cdota_name: Optional[str]
    ingame_alias: Optional[str]


class Item(InGameEntityBase, table=True):
    price: Optional[int]


# Leagues, Teams and Players
class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: str


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    odota_id: int
    name: str


class League(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int
    name: str
    tier: int

    start_date: int  # unix time stamp
    end_date: int

    ended: bool

    match_id: Optional[int] = Field(default=None, foreign_key="team.id")
    match: Optional["Match"] = Relationship(back_populates="heroes")


# Matches and Games
# Game - a match from a player's perspective
class GameItemPurchaseLink(SQLModel, table=True):
    playergameinfo_id: Optional[int] = Field(
        default=None, foreign_key="playergameinfo.id", primary_key=True
    )
    item_id: Optional[int] = Field(
        default=None, foreign_key="item.id", primary_key=True
    )


class GameItemBackpackLink(SQLModel, table=True):
    playergameinfo_id: Optional[int] = Field(
        default=None, foreign_key="playergameinfo.id", primary_key=True
    )
    item_id: Optional[int] = Field(
        default=None, foreign_key="item.id", primary_key=True
    )


class InGamePosition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slot: int
    name: str


class PlayerGameInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team: Optional[int] = Field(default=None, foreign_key="team.id")
    player: Optional[int] = Field(default=None, foreign_key="player.id")
    nickname: str

    position: Optional[int] = Field(default=None, foreign_key="ingameposition.id")
    hero: Optional[int] = Field(default=None, foreign_key="hero.id")
    lane: int
    is_roaming: bool

    win: bool
    dire: bool

    rank: int
    apm: int
    slot_number: int
    pings: int

    purchases: List[Item] = Relationship(back_populates='game', link_model=GameItemPurchaseLink)
    backpack: List[Item] = Relationship(back_populates='game', link_model=GameItemBackpackLink)

    match: Optional["match"] = Relationship(back_populates="slot")
    match_id: Optional[int] = Field(default=None, foreign_key="match.id")


class Patch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    odota_id: int
    name: str


class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    match_id: int
    league = Field(default=None, foreign_key='league.id')

    patch = Field(default=None, foreign_key='patch.id')

    radiant: Optional[int] = Field(default=None, foreign_key="team.id")
    dire: Optional[int] = Field(default=None, foreign_key="team.id")
    radiant_win: bool

    players_info: List["PlayerGameInfo"] = Relationship(back_populates="match")

    total_draft_time: int
    radiant_draft_time: int
    dire_draft_time: int

    game_start_time: int  # unix timestamp
    duration: int
    replay_url: str


class WindowComparisonType(SQLModel,  table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Carry => [carry, offlane] / mid to mid / soft support => [hard support, soft support]

class WindowType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Base values / percentage
    comparison: Optional[int] = Field(default=None, foreign_key="WindowComparisonType.id")

class WindowInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wtype: Optional[int] = Field(default=None, foreign_key="WindowType.id")
    name: str
    description: str

class PlayerPerformanceWindowStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    window_info: Optional[int] = Field(default=None, foreign_key="WindowInfo.id")

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

    matchdata: Optional[int] = Field(default=None, foreign_key="playermatchdata.id")
    matchdata_id: Optional["PlayerMatchData"] = Relationship(back_populates="stats_window")


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

    first_death_time: int
    first_kill_time: int
    first_blood: int
    died_first: int

    matchdata_id: Optional[int] = Field(default=None, foreign_key="playermatchdata.id")
    matchdata: Optional["PlayerMatchData"] = Relationship(back_populates="stats_total")


class InGameBuildingLane(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    lane: str
    lane_num: int


class InGameBuildingTower(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tier: int


class InGameBarracks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    melee: bool


class InGameBuilding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    is_tower: bool  # or rax

    lane: Optional[int] = Field(default=None, foreign_key="InGameBuildingLane.id")

    tower: Optional[int] = Field(default=None, foreign_key="InGameBuildingTower.id")
    rax: Optional[int] = Field(default=None, foreign_key="InGameBarracks.id")

    building_stats_id: Optional[int] = Field(default=None, foreign_key="BuildingStats.id")
    building_stats: Optional["BuildingStats"] = Relationship(back_populates="buildings_stats")


class InGameBuildingDestroyed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    building: Optional[int] = Field(default=None, foreign_key='ingamebuilding.id')
    death_time: int

    destruction_order: Optional[int]
    destruction_order_tower: Optional[int]
    destruction_order_rax: Optional[int]

    # additional rax info
    destroyed_lane_one: bool = Field(default=False)
    destroyed_lane_two: bool = Field(default=False)
    destroyed_lane_three: bool = Field(default=False)

    megacreeps: bool = Field(default=False)

    # additional tower info
    naked_throne: bool = Field(default=False)

    building_stats_id: Optional[int] = Field(default=None, foreign_key="BuildingStats.id")
    building_stats: Optional["BuildingStats"] = Relationship(back_populates="buildings_stats")


class BuildingStats(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)

    dire: bool

    buildings: List["InGameBuildingDestroyed"] = Relationship(back_populates="buildings_dead",
                                                              link_model=InGameBuildingDestroyed)
    buildings_not_dead: List["InGameBuilding"] = Relationship(back_populates="buildings_not_dead",
                                                              link_model=InGameBuilding)

    destruction_order: Optional[int]
    destruction_order_tower: Optional[int]
    destruction_order_rax: Optional[int]

    # additional rax info
    destroyed_lane: Optional[bool]
    megacreeps: Optional[bool]

    # additional tower info
    naked_throne: Optional[bool]


class BuildingStatsKillLink(SQLModel, table=True):
    buildingstats_id: Optional[int] = Field(
        default=None, foreign_key="BuildingStats.id", primary_key=True
    )
    team_buildings_kill: Optional[int] = Field(
        default=None, foreign_key="PlayerMatchData.id", primary_key=True
    )


class BuildingStatsLostLink(SQLModel, table=True):
    buildingstats_id: Optional[int] = Field(
        default=None, foreign_key="BuildingStats.id", primary_key=True
    )
    team_buildings_lost: Optional[int] = Field(
        default=None, foreign_key="PlayerMatchData.id", primary_key=True
    )


class AdditionalMatchStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    first_ten_kills_dire: bool
    first_roshan_dire: int
    first_roshan: int


class PlayerMatchData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key='league.id')
    match_id: Optional[int] = Field(default=None, foreign_key='match.id')
    player: Optional[int] = Field(default=None, foreign_key="player.id")
    player_game_info: Optional[int] = Field(default=None, foreign_key="playergameinfo.id")

    team_buildings_kill: List["BuildingStats"] = Relationship(back_populates="buildings_kill",
                                                              link_model=BuildingStatsKillLink)
    team_buildings_lost: List["BuildingStats"] = Relationship(back_populates="buildings_lost",
                                                              link_model=BuildingStatsLostLink)

    match_additional_stats: Optional[int] = Field(default=None, foreign_key="AdditionalMatchStats.id")
    player_window_stats: List["PlayerPerformanceWindowStats"] = Relationship(back_populates="match_data_window")
    player_total_stats: List["PlayerPerformanceTotalStats"] = Relationship(back_populates="match_data_total")
