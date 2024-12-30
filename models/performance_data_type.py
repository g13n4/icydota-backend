from datetime import datetime
from typing import Optional

from .helpers import _fk
from sqlalchemy.sql import text
from sqlmodel import Field, Relationship, SQLModel


# COMPARISON
class ComparisonType(SQLModel, table=True):
    __tablename__ = "comparison_types"

    id: Optional[int] = Field(default=None, primary_key=True)

    flat: bool = Field(index=True)  # percent or flat

    # if basic == True = pos 1 is compared to pos 1 and 3
    # if basic == False = pos 1 is compared to sum(1, 3) / 2
    basic: Optional[bool] = Field(default=True, index=True)

    # position/hero
    cpd_name_short: Optional[str]
    cps_name_short: Optional[str]

    # position/hero/player
    cpd_name: Optional[str]
    cps_name: Optional[str]

    player_cpd_id: Optional[int] = _fk("players", "account_id")
    player_cps_id: Optional[int] = _fk("players", "account_id")

    hero_cpd_id: Optional[int] = _fk("heroes")
    hero_cps_id: Optional[int] = _fk("heroes")

    pos_cpd_id: Optional[int] = _fk("positions")
    pos_cps_id: Optional[int] = _fk("positions")

    performance: Optional["GamePerformance"] = Relationship(back_populates="comparison")


# AGGREGATION
class DataAggregationType(SQLModel, table=True):
    __tablename__ = "data_aggregation_types"

    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)
    created_at: datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )

    # We can combine IDs to show that a hero can be flexed
    by_player: bool = Field(default=False, index=True)
    player_id: Optional[int] = _fk("players", "account_id")

    by_hero: bool = Field(default=False, index=True)
    hero_id: Optional[int] = _fk("heroes")

    by_position: bool = Field(default=False, index=True)
    position_id: Optional[int] = _fk("positions")

    performance: Optional["GamePerformance"] = Relationship(
        back_populates="aggregation"
    )


# CROSS COMPARISON
class CrossComparisonType(SQLModel, table=True):
    __tablename__ = "cross_comparison_types"

    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)
    created_at: datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )

    pos_player_cross: Optional[bool] = Field(default=False, index=True)
    pos_hero_cross: Optional[bool] = Field(default=False, index=True)

    sup_cross: Optional[bool] = Field(default=False, index=True)
    carry_cross: Optional[bool] = Field(default=False, index=True)
    mid_cross: Optional[bool] = Field(default=False, index=True)

    player_id: Optional[int] = _fk("players", "account_id")
    player_cross_cps_id: Optional[int] = _fk("players", "account_id")

    hero_id: Optional[int] = _fk("heroes")
    hero_cross_cps_id: Optional[int] = _fk("heroes")

    position_id: Optional[int] = _fk("positions")
    position_cross_cps_id: Optional[int] = _fk("positions")

    performance: Optional["GamePerformance"] = Relationship(
        back_populates="cross_comparison"
    )
