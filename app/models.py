from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import condecimal
import datetime

# Items and Heroes


class InGameEntityBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    odota_id: int
    name: str


class Hero(InGameEntityBase, table=True):
    pass


class Item(InGameEntityBase, table=True):
    pass


# Leagues, Teams and Players


class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: str


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class League(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int
    name: str
    tier: int

    start_date: datetime.timedelta
    end_date: datetime.timedelta

    ended: bool

# Matches and Games
# Game - a match from a player's perspective


class GameItemPurchaseLink(SQLModel, table=True):
    game_id: Optional[int] = Field(
        default=None, foreign_key="game.id", primary_key=True
    )
    item_id: Optional[int] = Field(
        default=None, foreign_key="item.id", primary_key=True
    )


class GameItemBackpackLink(SQLModel, table=True):
    game_id: Optional[int] = Field(
        default=None, foreign_key="game.id", primary_key=True
    )
    item_id: Optional[int] = Field(
        default=None, foreign_key="item.id", primary_key=True
    )


class Lane(SQLModel, table=True):
    """Lining (to minute 10) from the players perspective"""
    id: Optional[int] = Field(default=None, primary_key=True)


class Game(SQLModel, table=True):
    """A full game from the players perspective"""
    id: Optional[int] = Field(default=None, primary_key=True)

    kills: int
    assists: int
    deaths: int

    level: int
    total_xp: int
    xpm: int

    kda: int
    kpm: condecimal(max_digits=5, decimal_places=2) = Field(default=0)  # kills per minute
    hero_damage: int
    team_fight_participation: condecimal(max_digits=5, decimal_places=2) = Field(default=0)

    creeps_stacked: int

    creep_denies: int
    last_hits: int
    creep_kills: int   # lane_kills
    neutral_kills: int
    ancient_kills: int
    observer_kills: int
    sentry_kills: int
    dewards: int  # ? observer_kills + sentry_kills

    net_worth: int
    gold_spent: int
    gold_earned: int  # total gold
    purchases: List[Item] = Relationship(back_populates='game', link_model=GameItemPurchaseLink)
    gpm: int

    tower_damage: int

    pings: int
    apm: int

    rank: int

    runes: int

    backpack: List[Item] = Relationship(back_populates='game', link_model=GameItemBackpackLink)


class Slot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slot_number: int
    player: Optional[int] = Field(default=None, foreign_key="player.id")
    nickname: str
    position: int  # lane role
    hero: Optional[int] = Field(default=None, foreign_key="hero.id")
    win: bool

    lane: Optional[int] = Field(default=None, foreign_key="lane.id")
    game: Optional[int] = Field(default=None, foreign_key="game.id")

    match_id: Optional[int] = Field(default=None, foreign_key="match.id")
    match: List["match"] = Relationship(back_populates="slot")


class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int

    # radiant: Field(default=None, foreign_key="team.id")
    dire: Optional[int] = Field(default=None, foreign_key="team.id")
    radiant_win: bool

    slots: List["Slot"] = Relationship(back_populates="match")

    total_draft_time: int
    radiant_draft_time: int
    dire_draft_time: int
    duration: datetime.timedelta
    game_start_time: int  # unix timestamp
    replay_url: str

