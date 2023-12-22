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


class InGamePosition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: int
    name: str


class PlayerGameInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team: Optional[int] = Field(default=None, foreign_key="team.id")
    player: Optional[int] = Field(default=None, foreign_key="player.id")
    nickname: str

    position: Optional[int] = Field(default=None, foreign_key="InGamePosition.id")
    hero: Optional[int] = Field(default=None, foreign_key="hero.id")
    lane: int
    is_roaming: bool

    win: bool
    dire: bool

    rank: int
    apm: int
    slot_number: int
    pings: int

    game: Optional["Game"] = Relationship(back_populates="slot")
    game_id: Optional[int] = Field(default=None, foreign_key="game.id")


class Patch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    odota_id: int
    name: str


class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    match_id: int

    league: Optional[League] = Relationship(back_populates='games')
    league_id: Optional[int] = Field(default=None, foreign_key='league.id')

    patch = Field(default=None, foreign_key='patch.id')

    radiant: Optional[int] = Field(default=None, foreign_key="team.id")
    dire: Optional[int] = Field(default=None, foreign_key="team.id")
    radiant_win: bool

    players_info: List["PlayerGameInfo"] = Relationship(back_populates="game")

    total_draft_time: int
    radiant_draft_time: int
    dire_draft_time: int

    game_start_time: int  # unix timestamp
    duration: int
    replay_url: str


class WindowComparisonType(SQLModel, table=True):
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
    comparison: Optional[int] = Field(default=None, foreign_key="WindowComparisonType.id")
    info_type: Optional[int] = Field(default=None, foreign_key="WindowInfoType.id")
    description: Optional[str]
    name: str

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

    first_death_time: int
    first_kill_time: int
    first_blood: int
    died_first: int

    matchdata_id: Optional[int] = Field(default=None, foreign_key="PlayerGameData.id")
    matchdata: Optional["PlayerGameData"] = Relationship(back_populates="stats_total")


class InGameBuildingLane(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    lane_num: int


class InGameBarracks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    melee: bool
    name: str


class InGameBuilding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str

    lane: Optional[int] = Field(default=None, foreign_key="InGameBuildingLane.id")

    is_tower: bool  # or rax
    tier: Optional[int]
    tower4: Optional[bool]  # False - first, True - second one

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
        default=None, foreign_key="PlayerGameData.id", primary_key=True
    )


class BuildingStatsLostLink(SQLModel, table=True):
    buildingstats_id: Optional[int] = Field(
        default=None, foreign_key="BuildingStats.id", primary_key=True
    )
    team_buildings_lost: Optional[int] = Field(
        default=None, foreign_key="PlayerGameData.id", primary_key=True
    )


class AdditionalMatchStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    first_ten_kills_dire: bool
    first_roshan_dire: int
    first_roshan_time: int


class PlayerGameData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key='league.id')
    game_id: Optional[int] = Field(default=None, foreign_key='game.id')
    player: Optional[int] = Field(default=None, foreign_key="player.id")
    player_game_info: Optional[int] = Field(default=None, foreign_key="playergameinfo.id")

    team_buildings_kill: List["BuildingStats"] = Relationship(back_populates="buildings_kill",
                                                              link_model=BuildingStatsKillLink)
    team_buildings_lost: List["BuildingStats"] = Relationship(back_populates="buildings_lost",
                                                              link_model=BuildingStatsLostLink)

    match_additional_stats: Optional[int] = Field(default=None, foreign_key="AdditionalMatchStats.id")
    player_window_stats: List["PlayerPerformanceWindowStats"] = Relationship(back_populates="match_data_window")
    player_total_stats: List["PlayerPerformanceTotalStats"] = Relationship(back_populates="match_data_total")
