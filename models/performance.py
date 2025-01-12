from typing import List, Optional, ClassVar

from pydantic import condecimal
from sqlmodel import Field, Relationship, SQLModel

from constants.game_performance import GamePerformanceConstant
from constants.performance.total import TotalMeta
from constants.performance.window import WindowMeta
from modules.empty_mask_converter import EmptyMaskConverter

from .helpers import (
    SMALLINT_FIELD_NULLABLE,
    _fk,
    sa_kwargs_setter,
)
from .performance_fields_type import PerformanceWindowField


class GamePerformanceType(SQLModel, table=True):
    __tablename__ = "game_performance_types"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    description: Optional[str]
    is_active: bool = Field(default=True)

    const: ClassVar[object] = GamePerformanceConstant


class GamePerformance(SQLModel, table=True):
    __tablename__ = "games_performance"

    id: Optional[int] = Field(default=None, primary_key=True)

    performance_type_id: Optional[int] = _fk(
        "game_performance_types", col_type="smallint", index=True
    )
    performance_type: Optional["GamePerformanceType"] = Relationship(
        back_populates="gp"
    )


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
    aggregation_type: Optional["DataAggregationType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    window_data: List["PerformanceWindowData"] = Relationship(
        back_populates="game_performance",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True),
    )
    total_data: Optional["PerformanceTotalData"] = Relationship(
        back_populates="game_performance",
    )

    player_game_data_id: Optional[int] = Field(
        default=None, foreign_key="players_game_data.id", index=True
    )
    player_game_data: Optional["PlayerGameData"] = Relationship(
        back_populates="performance"
    )


# PERFORMANCE DATA
class PerformanceDataCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # damage / interval
    label: Optional[str]
    description: Optional[str]

    data_type: List["PerformanceDataCalculation"] = Relationship(
        back_populates="data_category",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    __tablename__ = "performance_data_categories"


class PerformanceDataCalculation(SQLModel, table=True):
    __tablename__ = "performance_data_types"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    is_active: bool = Field(default=True)

    system_name: Optional[str]

    data_category_id: Optional[int] = Field(
        default=None, foreign_key="performance_data_categories.id", index=True
    )
    data_category: Optional["PerformanceDataCategory"] = Relationship(
        back_populates="data_type",
    )


class PerformanceWindowData(SQLModel, table=True):
    __tablename__ = "performance_windows_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    data_type_id: Optional[int] = Field(
        default=None, foreign_key="performance_data_types.id", index=True
    )
    data_type: Optional["PerformanceDataCalculation"] = Relationship(back_populates="pwd")

    game_performance_id: Optional[int] = Field(
        default=None, foreign_key="games_performance.id", index=True
    )
    game_performance: Optional["GamePerformance"] = Relationship(
        back_populates="window_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )
    # Fields to work with empty space
    is_empty: bool = Field(default=False)
    l_empty_mask: int = SMALLINT_FIELD_NULLABLE
    g_empty_mask: int = SMALLINT_FIELD_NULLABLE

    performance_table_id: Optional[int] = Field(
        default=None, foreign_key="performance_windows_table.id", index=True
    )
    performance_table: Optional["PerformanceWindowTable"] = Relationship(
        back_populates="window_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )

    # @property
    # def get_window_data(self) -> "PerformanceWindowTable":
    #     if self.is_empty:
    #         empty_fields = {field: None for field in PerformanceWindowField.ALL}
    #         if self.l_empty_mask:
    #             empty_fields.update(
    #                 EmptyMaskConverter.convert_from_mask_to_dict(
    #                     self.l_empty_mask, PerformanceWindowField.LANE
    #                 )
    #             )
    #
    #         elif self.g_empty_mask:
    #             empty_fields.update(
    #                 EmptyMaskConverter.convert_from_mask_to_dict(
    #                     self.g_empty_mask, PerformanceWindowField.LANE
    #                 )
    #             )
    #         return PerformanceWindowTable(**empty_fields)
    #     else:
    #         return self.perfomance_table


class PerformanceWindowTable(SQLModel, table=True, metaclass=WindowMeta):
    __tablename__ = "performance_windows_table"

    id: Optional[int] = Field(default=None, primary_key=True)


# PERFORMANCE TOTAL
class PerformanceTotalData(SQLModel, table=True, metaclass=TotalMeta):
    __tablename__ = "performance_totals_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    game_performance_id: Optional[int] = Field(
        default=None, foreign_key="games_performance.id", index=True
    )
    game_performance: Optional["GamePerformance"] = Relationship(
        back_populates="total_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )
