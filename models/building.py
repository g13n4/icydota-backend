from typing import List, Optional

from .helpers import _fk
from sqlmodel import Field, Relationship, SQLModel


# BUILDINGS
class Building(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str

    lane: int

    is_tower: bool  # or rax
    tier: Optional[int]
    tower4: Optional[bool]  # False - first, True - second one

    is_rax: Optional[bool]
    melee: Optional[bool]

    __tablename__ = "in_game_buildings"


class BuildingDestroyed(SQLModel, table=True):
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

    building_data_id: Optional[int] = Field(
        default=None, foreign_key="buildings_data.id"
    )
    building_data: Optional["BuildingData"] = Relationship(
        back_populates="destruction_order"
    )

    __tablename__ = "in_game_buildings_destroyed"


class BuildingNotDestroyed(SQLModel, table=True):
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

    building_data: Optional["BuildingData"] = Relationship(
        back_populates="not_destroyed"
    )

    __tablename__ = "in_game_buildings_not_destroyed"


class BuildingData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    dire: bool

    destruction_order: List["InGameBuildingDestroyed"] = Relationship(
        back_populates="building_data"
    )

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

    not_destroyed: Optional["InGameBuildingNotDestroyed"] = Relationship(
        back_populates="building_data"
    )
    not_destroyed_id: Optional[int] = Field(
        default=None, foreign_key="in_game_buildings_not_destroyed.id"
    )

    __tablename__ = "buildings_data"
