from datetime import datetime
from typing import List, Optional, ClassVar

import sqlalchemy as db
from sqlalchemy import ForeignKey
from sqlalchemy.sql import text
from sqlmodel import Field, Relationship, SQLModel

from constants.performance.game_side import SidePerformance
from models.helpers import _fk
from models.mixins.game_performance_graph import GamePerformanceGraphMixin
from models.mixins.helpers import inherit_annotations
from models.mixins.side_performance import SidePerformanceDataMixin


@inherit_annotations
class SidePerformanceData(SidePerformanceDataMixin, SQLModel, table=True):
    __tablename__ = "sides_performance_data"

    const: ClassVar[SidePerformance] = SidePerformance

    id: int = Field(default=None, primary_key=True)

    game_id: int = Field(
        sa_column=db.Column(
            db.BIGINT,
            ForeignKey("games.id", ondelete="CASCADE"),
            nullable=True, primary_key=False, index=False
        )
    )

    game: Optional["Game"] = Relationship(back_populates="sides_performance")

    dire: bool


class Game(SQLModel, table=True):
    __tablename__ = "games"

    id: int = Field(
        sa_column=db.Column(db.BIGINT, nullable=False, primary_key=True, index=True),
    )  # match_id

    name: Optional[str]
    processed_counter: int

    league: "League" = Relationship(back_populates="games")
    league_id: int = Field(default=None, foreign_key="leagues.id", index=True)

    patch_id: int = Field(default=None, foreign_key="patches.id")

    sent_team_id: int = _fk("teams")
    dire_team_id: int = _fk("teams")
    dire_win: Optional[bool]

    players_game_data: List["PlayerGameData"] = Relationship(
        back_populates="game",
        cascade_delete=True,
    )

    average_roshan_window_time: Optional[int]
    roshan_death: List["RoshanDeath"] = Relationship(
        back_populates="game",
        cascade_delete=True,
    )

    first_ten_kills_dire: Optional[bool]
    hero_death: List["HeroDeath"] = Relationship(
        back_populates="game",
        cascade_delete=True,
    )

    dire_lost_first_tower: Optional[bool]

    building_data: List["BuildingData"] = Relationship(
        back_populates="game",
        cascade_delete=True,
    )

    sides_performance: List[SidePerformanceData] = Relationship(
        back_populates="game",
        cascade_delete=True,
    )

    graph: Optional["GamePerformanceGraph"] = Relationship(back_populates="game")

    game_start_time: int = Field(
        sa_column=db.Column(db.BIGINT, nullable=True, unique=False),
    )  # unix timestamp
    duration: Optional[int]
    replay_url: str

    is_broken: Optional[bool] = Field(default=False)


class PlayerGameData(SQLModel, table=True):
    __tablename__ = "players_game_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    invalid: Optional[bool]

    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    player_id: Optional[int] = Field(default=None, foreign_key="players.account_id")

    original_position: Optional[int] = Field(default=None)
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

    game_id: Optional[int] = _fk("games", col_type="bigint", index=True, cascade=True)
    game: Optional["Game"] = Relationship(back_populates="players_game_data")

    performance: List["Performance"] = Relationship(
        back_populates="player_game_data",
        cascade_delete=True,
    )

    invalid: Optional[bool]

    created_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )


class Patch(SQLModel, table=True):
    __tablename__ = "patches"

    id: int = Field(default=None, primary_key=True)
    name: Optional[str]
    date: Optional[datetime] = Field(default=None, nullable=True)

    aggregation_allowed: bool = Field(default=False, nullable=False)

    processed_at: Optional[datetime] = Field(default=None)


class GamePerformanceGraph(GamePerformanceGraphMixin, SQLModel, table=True):
    __tablename__ = "game_performance_graphs"

    id: int = Field(default=None, primary_key=True)

    game_id: int = Field(
        sa_column=db.Column(
            db.BIGINT,
            ForeignKey("games.id", ondelete="CASCADE"),
            nullable=True, primary_key=False, index=False
        )
    )
    game: Optional["Game"] = Relationship(back_populates="graph")
