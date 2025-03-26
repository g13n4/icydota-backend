from typing import List, Optional, ClassVar

import sqlalchemy as db
from sqlmodel import Field, Relationship, SQLModel

from constants.abilities.total import AbilityTotals
from constants.calculation.game.calculation_types import WindowCalculations
from constants.calculation.game.category import WindowCategories
from constants.game_performance import PerformanceTypeConstant
from constants.performance.total import GameTotals
from constants.performance.window import AllWindows
from .helpers import (
    _fk,
    sa_kwargs_setter,
)
from .mixins.abilities import AbilityTotalDataMixin
from .mixins.helpers import inherit_annotations
from .mixins.totals import PerformanceTotalDataMixin
from .mixins.windows import PerformanceWindowTableMixin


OFFSET = 1


# TODO: Delete this version of db and create a new one

class Performance(SQLModel, table=True):
    __tablename__ = "performances"

    const: ClassVar[PerformanceTypeConstant] = PerformanceTypeConstant

    id: Optional[int] = Field(default=None, primary_key=True)

    type_id: int = Field(sa_column=db.Column(db.SMALLINT, primary_key=False))

    # TYPE INFORMATION DATA
    cross_comparison_id: Optional[int] = _fk(
        "cross_comparison_types", col_type="smallint"
    )
    cross_comparison_type: Optional["CrossComparisonType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    comparison_id: Optional[int] = Field(
        default=None, foreign_key="comparison_types.id"
    )
    comparison_type: Optional["ComparisonType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    aggregation_id: Optional[int] = Field(
        default=None, foreign_key="data_aggregation_types.id"
    )
    aggregation_type: Optional["AggregationType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    by_team_id: Optional[int] = Field(
        default=None, foreign_key="by_team_types.id"
    )
    by_team_type: Optional["ByTeamType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    # PERFORMANCE DATA
    window_data: List["PerformanceWindowData"] = Relationship(
        back_populates="game_performance",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True),
    )
    total_data: Optional["PerformanceTotalData"] = Relationship(
        back_populates="game_performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        }
    )
    ability_total_data: Optional["AbilityTotalData"] = Relationship(
        back_populates="game_performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        }
    )

    player_game_data_id: Optional[int] = Field(
        default=None, foreign_key="players_game_data.id"
    )
    player_game_data: Optional["PlayerGameData"] = Relationship(
        back_populates="performance"
    )


# PERFORMANCE DATA
class PerformanceWindowCalculationCategory(SQLModel, table=True):
    __tablename__ = "performance_window_calculation_categories"

    const: ClassVar[WindowCategories] = WindowCategories

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str  # damage / interval
    label: Optional[str]
    description: Optional[str]

    data_type: List["PerformanceWindowCalculationType"] = Relationship(
        back_populates="data_category",
        sa_relationship_kwargs={ "lazy": "selectin" },
    )


class PerformanceWindowCalculationType(SQLModel, table=True):
    __tablename__ = "performance_window_calculation_types"

    const: ClassVar[WindowCalculations] = WindowCalculations

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str

    is_active: bool = Field(default=True)

    description: Optional[str]

    data_category_id: Optional[int] = Field(
        default=None, foreign_key="performance_window_calculation_categories.id", index=True
    )
    category: Optional["PerformanceWindowCalculationCategory"] = Relationship(
        back_populates="calculation_type",
    )


class PerformanceWindowData(SQLModel, table=True):
    __tablename__ = "performance_windows_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    data_calculation_id: Optional[int] = Field(
        default=None, foreign_key="performance_window_calculation_types.id", index=True
    )
    calc_type: Optional["PerformanceWindowCalculationType"] = Relationship(back_populates="pwct")

    performance_id: Optional[int] = Field(
        default=None, foreign_key="performances.id", index=True
    )
    performance: Optional["Performance"] = Relationship(
        back_populates="window_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )

    # Fields to work with empty space
    l_empty_mask: Optional[int] = Field(sa_column=db.Column(db.SMALLINT, primary_key=False, nullable=True))
    g_empty_mask: Optional[int] = Field(sa_column=db.Column(db.SMALLINT, primary_key=False, nullable=True))

    performance_table_id: Optional[int] = Field(
        default=None, foreign_key="performance_windows_table.id"
    )
    performance_table: Optional["PerformanceWindowTable"] = Relationship(
        back_populates="window_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )

@inherit_annotations
class PerformanceWindowTable(PerformanceWindowTableMixin, SQLModel, table=True):
    __tablename__ = "performance_windows_table"

    const: ClassVar[AllWindows] = AllWindows

    id: Optional[int] = Field(default=None, primary_key=True)


# PERFORMANCE TOTAL
@inherit_annotations
class PerformanceTotalData(PerformanceTotalDataMixin, SQLModel, table=True):
    __tablename__ = "performance_totals_data"

    const: ClassVar[GameTotals] = GameTotals

    id: Optional[int] = Field(default=None, primary_key=True)

    performance_id: Optional[int] = Field(
        default=None, foreign_key="performances.id"
    )
    game_performance: Optional["Performance"] = Relationship(
        back_populates="total_data",
    )


# ABILITY  DATA
@inherit_annotations
class AbilityTotalData(AbilityTotalDataMixin, SQLModel, table=True):
    __tablename__ = "ability_performance_data"

    const: ClassVar[AbilityTotals] = AbilityTotals

    id: Optional[int] = Field(default=None, primary_key=True)

    performance_id: Optional[int] = Field(
        default=None, foreign_key="performances.id"
    )
    performance: Optional["Performance"] = Relationship(
        back_populates="ability_data",
    )
