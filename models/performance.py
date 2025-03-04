from typing import List, Optional, ClassVar

from sqlmodel import Field, Relationship, SQLModel

from constants.calculation.game.calculation_types import WindowCalculations
from constants.calculation.game.category import WindowCategories
from constants.game_performance import PerformanceTypeConstant
from models.metaclasses import WindowMeta, TotalMeta, AbilityTotalMeta

from .helpers import (
    SMALLINT_FIELD_NULLABLE,
    _fk,
    sa_kwargs_setter,
)


OFFSET = 1


class Performance(SQLModel, table=True):
    __tablename__ = "performances"

    const: ClassVar[PerformanceTypeConstant] = PerformanceTypeConstant

    id: Optional[int] = Field(default=None, primary_key=True)

    type_id: int

    # TYPE INFORMATION DATA
    cross_comparison_id: Optional[int] = _fk(
        "cross_comparison_types", col_type="smallint", index=True
    )
    cross_comparison_type: Optional["CrossComparisonType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    comparison_id: Optional[int] = Field(
        default=None, foreign_key="comparison_types.id", index=True
    )
    comparison_type: Optional["ComparisonType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    aggregation_id: Optional[int] = Field(
        default=None, foreign_key="data_aggregation_types.id", index=True
    )
    aggregation_type: Optional["AggregationType"] = Relationship(
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
        default=None, foreign_key="players_game_data.id", index=True
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
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class PerformanceWindowCalculationType(SQLModel, table=True):
    __tablename__ = "performance_window_calculation_types"

    const: ClassVar[WindowCalculations] = WindowCalculations

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    is_active: bool = Field(default=True)

    description: Optional[str]

    data_category_id: Optional[int] = Field(
        default=None, foreign_key="performance_data_categories.id", index=True
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

    game_performance_id: Optional[int] = Field(
        default=None, foreign_key="performances.id", index=True
    )
    performance: Optional["Performance"] = Relationship(
        back_populates="window_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )

    # Fields to work with empty space
    l_empty_mask: Optional[int] = SMALLINT_FIELD_NULLABLE
    g_empty_mask: Optional[int] = SMALLINT_FIELD_NULLABLE

    performance_table_id: Optional[int] = Field(
        default=None, foreign_key="performance_windows_table.id", index=True
    )
    performance_table: Optional["PerformanceWindowTable"] = Relationship(
        back_populates="window_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )


class PerformanceWindowTable(SQLModel, table=True, metaclass=WindowMeta):
    __tablename__ = "performance_windows_table"

    id: Optional[int] = Field(default=None, primary_key=True)


# PERFORMANCE TOTAL
class PerformanceTotalData(SQLModel, table=True, metaclass=TotalMeta):
    __tablename__ = "performance_totals_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    game_performance_id: Optional[int] = Field(
        default=None, foreign_key="performances.id", index=True
    )
    game_performance: Optional["Performance"] = Relationship(
        back_populates="total_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )


# ABILITY  DATA
class AbilityTotalData(SQLModel, table=True, metaclass=AbilityTotalMeta):
    __tablename__ = "ability_performance_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    performance_id: Optional[int] = Field(
        default=None, foreign_key="performances.id", index=True
    )
    performance: Optional["Performance"] = Relationship(
        back_populates="ability_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )
