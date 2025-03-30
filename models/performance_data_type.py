from datetime import datetime
from typing import Optional
import sqlalchemy as db
from sqlalchemy.sql import text
from sqlmodel import Field, Relationship, SQLModel
from typing_extensions import ClassVar

from constants.aggregation import AggregationConstant
from constants.calculation.cross_comparison import CrossComparisonConstant
from .helpers import _fk


# COMPARISON
class ComparisonType(SQLModel, table=True):
    __tablename__ = "comparison_types"

    id: int = Field(
        sa_column=db.Column(db.SMALLINT, nullable=False, primary_key=True, index=True),
    )

    # if is_flat we subtract comparans from comparandum and if it's not we divide thus operating in percents
    # can be none if it's a basic cross-comparison
    is_flat: Optional[bool] = Field(index=True)  # percent or is_flat

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

    hero_cpd_id: Optional[int] = _fk("heroes", col_type="smallint")
    hero_cps_id: Optional[int] = _fk("heroes", col_type="smallint")

    facet_cpd_id: Optional[int] = _fk("facets", col_type="smallint")
    facet_cps_id: Optional[int] = _fk("facets", col_type="smallint")

    pos_cpd_id: Optional[int] = _fk("positions", col_type="smallint")
    pos_cps_id: Optional[int] = _fk("positions", col_type="smallint")

    performance_id: Optional[int] = Field(default=None, foreign_key="performances.id", ondelete="CASCADE", )
    performance: Optional["Performance"] = Relationship(
        back_populates="comparison_type",
    )

# AGGREGATION
class AggregationType(SQLModel, table=True):
    __tablename__ = "data_aggregation_types"

    id: int = Field(
        sa_column=db.Column(db.SMALLINT, nullable=False, primary_key=True, index=True),
    )

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)
    patch_id: Optional[int] = Field(default=None, foreign_key="patches.id", index=True)

    created_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )
    # get from const
    type_id: int
    # We can combine IDs to show that a hero can be flexed
    player_id: Optional[int] = _fk("players", "account_id")

    hero_id: Optional[int] = _fk("heroes", col_type="smallint")
    facet_id: Optional[int] = _fk("facets", col_type="smallint")

    position_id: Optional[int] = _fk("positions", col_type="smallint")

    performance_id: Optional[int] = Field(default=None, foreign_key="performances.id", ondelete="CASCADE", )
    performance: Optional["Performance"] = Relationship(
        back_populates="aggregation_type",
    )

    const: ClassVar[AggregationConstant] = AggregationConstant


# CROSS COMPARISON
class CrossComparisonType(SQLModel, table=True):
    __tablename__ = "cross_comparison_types"

    id: int = Field(
        sa_column=db.Column(db.SMALLINT, nullable=False, primary_key=True, index=True),
    )

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)
    created_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )

    type_id: int
    position_aggregation_id: int

    performance_id: Optional[int] = Field(default=None, foreign_key="performances.id", ondelete="CASCADE", )
    performance: Optional["Performance"] = Relationship(
        back_populates="cross_comparison_type",
    )

    const: ClassVar[CrossComparisonConstant] = CrossComparisonConstant


class ByTeamType(SQLModel, table=True):
    __tablename__ = "by_team_types"

    id: int = Field(
        sa_column=db.Column(db.SMALLINT, nullable=False, primary_key=True, index=True),
    )

    patch_id: Optional[int] = Field(default=None, foreign_key="patches.id")
    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)
    match_id: Optional[int] = _fk('games', col_type='bigint')
    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")

    created_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )

    is_flat: Optional[bool] = Field(index=True)

    team_cpd_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    team_cps_id: Optional[int] = Field(default=None, foreign_key="teams.id")

    performance_id: Optional[int] = Field(default=None, foreign_key="performances.id", ondelete="CASCADE", )
    performance: Optional["Performance"] = Relationship(
        back_populates="by_team_type",
    )
