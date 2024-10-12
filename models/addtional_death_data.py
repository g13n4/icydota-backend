from typing import Optional

from helpers import _fk
from sqlmodel import Field, Relationship, SQLModel


class RoshanDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]

    game_id: Optional[int] = _fk("games", col_type="bigint")
    game: Optional["Game"] = Relationship(back_populates="roshan_death")

    __tablename__ = "roshan_deaths"


class HeroDeath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    death_number: int
    death_time: int

    kill_dire: Optional[bool]
    killer_hero_id: Optional[int] = _fk("heroes")
    killer_player_id: Optional[int] = _fk("players", "account_id")

    victim_dire: Optional[bool]
    victim_hero_id: Optional[int] = _fk("heroes")
    victim_player_id: Optional[int] = _fk("players", "account_id")

    game_id: Optional[int] = _fk("games", col_type="bigint")
    game: Optional["Game"] = Relationship(back_populates="hero_death")

    __tablename__ = "hero_deaths"
