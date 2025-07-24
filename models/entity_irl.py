import datetime
from typing import List, Optional, ClassVar

import sqlalchemy as db

from constants.position import PositionConstant
from models.helpers import sa_kwargs_setter
from sqlmodel import Field, Relationship, SQLModel


class Position(SQLModel, table=True):
    __tablename__ = "positions"

    id: int = Field(sa_column=db.Column(db.SMALLINT, primary_key=True))  # position number
    name: str

    const: ClassVar[PositionConstant] = PositionConstant


class Player(SQLModel, table=True):
    __tablename__ = "players"

    nickname: str

    account_id: int = Field(default=None, primary_key=True)
    steam_id: Optional[int] = Field(
        sa_column=db.Column(db.BIGINT, nullable=True, unique=True),
    )

    official_name: Optional[bool] = Field(default=False)


class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: int = Field(default=None, primary_key=True)  # open_dota id
    logo_url: Optional[str]
    name: str
    tag: str


class League(SQLModel, table=True):
    __tablename__ = "leagues"

    id: int = Field(default=None, primary_key=True, index=True)  # steam league id

    pd_link: Optional[str]
    name: Optional[str]
    tier: Optional[int]

    start_date: Optional[int]  # unix time stamp
    end_date: Optional[int]
    has_dates: bool = Field(default=False)

    has_started: Optional[bool] = Field(default=None)
    has_ended: Optional[bool] = Field(default=None)

    # if it's more than 8 days we stop checking
    new_game_found_at: Optional[datetime.datetime] = Field(default=None)

    processed_at: Optional[datetime.datetime] = Field(default=None)

    games: List["Game"] = Relationship(
        back_populates="league",
        sa_relationship_kwargs=sa_kwargs_setter(
            False, "cascade", "lazy", order_by="Game.id", join_depth=4
        ),
    )
