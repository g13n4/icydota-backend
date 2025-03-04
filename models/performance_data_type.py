from datetime import datetime
from typing import Optional

from typing_extensions import ClassVar

from constants.aggregation import AggregationConstant
from .helpers import _fk
from sqlalchemy.sql import text
from sqlmodel import Field, Relationship, SQLModel


# COMPARISON
class ComparisonType(SQLModel, table=True):
    __tablename__ = "comparison_types"

    id: Optional[int] = Field(default=None, primary_key=True)

    # if is_flat we subtract comparans from comparandum and if it's not we divide thus operating in percents
    is_flat: bool = Field(index=True)  # percent or is_flat

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

    facet_cpd_id: Optional[int] = _fk("facets")
    facet_cps_id: Optional[int] = _fk("facets")

    pos_cpd_id: Optional[int] = _fk("positions")
    pos_cps_id: Optional[int] = _fk("positions")

    performance: Optional["Performance"] = Relationship(back_populates="comparison")


# AGGREGATION
class AggregationType(SQLModel, table=True):
    __tablename__ = "data_aggregation_types"

    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)
    patch_id: Optional[int] = Field(default=None, foreign_key="patches.id", index=True)
    
    created_at: datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )
    # get from const
    type_id: int
    # We can combine IDs to show that a hero can be flexed
    player_id: Optional[int] = _fk("players", "account_id")

    hero_id: Optional[int] = _fk("heroes")
    facet_id: Optional[int] = _fk("facets")

    position_id: Optional[int] = _fk("positions")

    performance: Optional["Performance"] = Relationship(
        back_populates="aggregation"
    )
    const: ClassVar[AggregationConstant] = AggregationConstant


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

    facet_id: Optional[int] = _fk("facets")
    facet_cps_id: Optional[int] = _fk("facets")

    position_id: Optional[int] = _fk("positions")
    position_cross_cps_id: Optional[int] = _fk("positions")

    performance: Optional["Performance"] = Relationship(
        back_populates="cross_comparison"
    )
