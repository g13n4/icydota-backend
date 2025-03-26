from datetime import datetime
from typing import List, Optional, ClassVar

import sqlalchemy as db
from sqlalchemy.sql import text
from sqlmodel import Field, Relationship, SQLModel

from constants.performance.game_side import SidePerformance
from models.helpers import _fk, sa_kwargs_setter
from models.mixins.helpers import inherit_annotations
from models.mixins.side_performance import SidePerformanceDataMixin

@inherit_annotations
class SidePerformanceData(SidePerformanceDataMixin, SQLModel, table=True):
    __tablename__ = "sides_performance_data"

    const: ClassVar[SidePerformance] = SidePerformance

    id: int = Field(default=None, primary_key=True, index=True)

    game_id: int = Field(
        sa_column=db.Column(db.BIGINT, nullable=False, primary_key=False, index=False),
    )

    dire: bool


class Game(SQLModel, table=True):
    id: int = Field(
        sa_column=db.Column(db.BIGINT, nullable=False, primary_key=True, index=True),
    )  # match_id

    name: Optional[str]
    processed_counter: int

    league: Optional["League"] = Relationship(back_populates="games")
    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)

    patch_id: Optional[int] = Field(default=None, foreign_key="patches.id")

    sent_team_id: int = _fk("teams")
    dire_team_id: int = _fk("teams")
    dire_win: bool

    players_game_data: List["PlayerGameData"] = Relationship(
        back_populates="game",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True)
    )

    average_roshan_window_time: Optional[int]
    roshan_death: List["RoshanDeath"] = Relationship(
        back_populates="game",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True),
    )

    first_ten_kills_dire: bool
    hero_death: List["HeroDeath"] = Relationship(
        back_populates="game",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True),
    )

    dire_lost_first_tower: bool
    dire_building_status_id: Optional[int] = Field(
        default=None, foreign_key="buildings_data.id"
    )
    sent_building_status_id: Optional[int] = Field(
        default=None, foreign_key="buildings_data.id"
    )

    sent_performance_id: Optional[int] = _fk(
        "sides_performance_data", cascade=True
    )
    dire_performance_id: Optional[int] = _fk(
        "sides_performance_data", cascade=True
    )

    game_start_time: int = Field(
        sa_column=db.Column(db.BIGINT, nullable=False, unique=False),
    )  # unix timestamp
    duration: int
    replay_url: str

    broken_replay: Optional[bool]
    assumed_positions: Optional[bool]
    final_processing: Optional[bool]

    __tablename__ = "games"


class PlayerGameData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    player_id: Optional[int] = Field(default=None, foreign_key="players.account_id")

    position_id: Optional[int] = Field(default=None, foreign_key="positions.id")
    hero_id: Optional[int] = Field(default=None, foreign_key="heroes.id")
    facet_id: Optional[int] = Field(default=None, foreign_key="facets.id")

    slot: int

    name: Optional[str]
    name_short: Optional[str]

    lane: int
    is_roaming: bool

    win: bool
    dire: bool

    rank: Optional[int]
    apm: int
    pings: int

    game_id: Optional[int] = _fk("games", col_type="bigint", index=True)
    game: Optional["Game"] = Relationship(back_populates="players_data")

    performance: List["Performance"] = Relationship(
        back_populates="player_game_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True),
    )

    created_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )

    __tablename__ = "players_game_data"


class Patch(SQLModel, table=True):
    __tablename__ = "patches"

    id: int = Field(default=None, primary_key=True)  # open_dota id
    name: str
    date: datetime = Field(default=None, nullable=True)
