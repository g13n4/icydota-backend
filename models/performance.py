from typing import List, Optional, ClassVar

import sqlalchemy as db
from sqlmodel import Field, Relationship, SQLModel

from constants.abilities.total import AbilityTotals
from constants.calculation.game.calculation_types import WindowCalculations
from constants.calculation.game.category import WindowCategories
from constants.game_performance import PerformanceTypeConstant
from constants.performance.total.total import GameTotals
from constants.performance.window import AllWindows
from .mixins.abilities import AbilityTotalDataMixin
from .mixins.helpers import inherit_annotations
from .mixins.totals import PerformanceTotalDataMixin
from .mixins.windows import PerformanceWindowTableMixin


OFFSET = 1


class Performance(SQLModel, table=True):
    __tablename__ = "performances"

    const: ClassVar[PerformanceTypeConstant] = PerformanceTypeConstant

    id: Optional[int] = Field(default=None, primary_key=True)

    outdated: bool = Field(default=False, index=True)
    type_id: int = Field(sa_column=db.Column(db.SMALLINT, primary_key=False, index=True))

    # TYPE INFORMATION DATA
    cross_comparison_type: Optional["CrossComparisonType"] = Relationship(
        back_populates="performance",
        cascade_delete=True,
    )

    comparison_type: Optional["ComparisonType"] = Relationship(
        back_populates="performance",
        cascade_delete=True,
    )

    aggregation_type: Optional["AggregationType"] = Relationship(
        back_populates="performance",
        cascade_delete=True,
    )

    by_team_type: Optional["ByTeamType"] = Relationship(
        back_populates="performance",
        cascade_delete=True,
    )

    # PERFORMANCE DATA
    window_data: List["PerformanceWindowData"] = Relationship(
        back_populates="performance",
        cascade_delete=True,
    )
    total_data: Optional["PerformanceTotalData"] = Relationship(
        back_populates="performance",
        cascade_delete=True,
    )
    ability_data: Optional["AbilityTotalData"] = Relationship(
        back_populates="performance",
    )

    player_game_data_id: Optional[int] = Field(
        default=None, foreign_key="players_game_data.id", ondelete="CASCADE",
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

    calc_type: List["PerformanceWindowCalculationType"] = Relationship(
        back_populates="calc_category",
        sa_relationship_kwargs={ "lazy": "selectin" },
    )


class PerformanceWindowCalculationType(SQLModel, table=True):
    __tablename__ = "performance_window_calculation_types"

    const: ClassVar[WindowCalculations] = WindowCalculations

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str

    is_active: bool = Field(default=True)

    description: Optional[str]

    calc_category_id: Optional[int] = Field(
        default=None, foreign_key="performance_window_calculation_categories.id", index=True
    )
    calc_category: Optional["PerformanceWindowCalculationCategory"] = Relationship(
        back_populates="calc_type",
    )


class PerformanceWindowData(SQLModel, table=True):
    __tablename__ = "performance_windows_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    calc_type_id: Optional[int] = Field(
        default=None, foreign_key="performance_window_calculation_types.id", index=True
    )

    performance_id: Optional[int] = Field(
        default=None, foreign_key="performances.id", ondelete="CASCADE",
    )
    performance: Optional["Performance"] = Relationship(
        back_populates="window_data",
    )

    # Fields to work with empty space
    l_empty_mask: Optional[int] = Field(sa_column=db.Column(db.SMALLINT, primary_key=False, nullable=True))
    g_empty_mask: Optional[int] = Field(sa_column=db.Column(db.SMALLINT, primary_key=False, nullable=True))

    performance_table_id: Optional[int] = Field(
        default=None, foreign_key="performance_windows_table.id", ondelete="CASCADE",
    )
    performance_table: Optional["PerformanceWindowTable"] = Relationship(
        back_populates="window_data",
    )


@inherit_annotations
class PerformanceWindowTable(PerformanceWindowTableMixin, SQLModel, table=True):
    __tablename__ = "performance_windows_table"

    const: ClassVar[AllWindows] = AllWindows

    id: Optional[int] = Field(default=None, primary_key=True)

    window_data: Optional["PerformanceWindowData"] = Relationship(
        back_populates="performance_table",
    )


# PERFORMANCE TOTAL
@inherit_annotations
class PerformanceTotalData(PerformanceTotalDataMixin, SQLModel, table=True):
    __tablename__ = "performance_totals_data"

    const: ClassVar[GameTotals] = GameTotals

    id: Optional[int] = Field(default=None, primary_key=True)

    performance_id: Optional[int] = Field(default=None, foreign_key="performances.id", ondelete="CASCADE", )
    performance: Optional["Performance"] = Relationship(
        back_populates="total_data",
    )


# ABILITY  DATA
@inherit_annotations
class AbilityTotalData(AbilityTotalDataMixin, SQLModel, table=True):
    __tablename__ = "ability_performance_data"

    const: ClassVar[AbilityTotals] = AbilityTotals

    id: Optional[int] = Field(default=None, primary_key=True)

    performance_id: Optional[int] = Field(default=None, foreign_key="performances.id", ondelete="CASCADE", )
    performance: Optional["Performance"] = Relationship(
        back_populates="ability_data",
    )
