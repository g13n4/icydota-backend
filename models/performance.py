from typing import List, Optional

from helpers import (
    SMALLINT_FIELD_NULLABLE,
    _fk,
    sa_kwargs_setter,
)
from performance_fields_type import PerformanceWindowField
from pydantic import condecimal
from sqlmodel import Field, Relationship, SQLModel

from modules.empty_mask_converter import EmptyMaskConverter


class GamePerformanceType(SQLModel, table=True):
    __tablename__ = "game_performance_types"

    id: Optional[int] = Field(default=None, primary_key=True)

    MATCH_DATA = 1
    MATCH_DATA_COMPARISON = 2
    AGGREGATION = 3
    AGGREGATION_COMPARISON = 4
    COMBINED_AGGREGATION = 5
    COMBINED_AGGREGATION_COMPARISON = 6
    CROSS_COMPARISON = 7

    TYPES = [
        (MATCH_DATA, "Match Data"),
        (MATCH_DATA_COMPARISON, "Match Data Comparison"),
        (AGGREGATION, "Aggregation"),
        (AGGREGATION_COMPARISON, "Aggregation Comparison"),
        (COMBINED_AGGREGATION, "Combined Aggregation"),
        (COMBINED_AGGREGATION_COMPARISON, "Combined Aggregation Comparison"),
        (CROSS_COMPARISON, "Cross Comparison"),
    ]

    name: str
    description: Optional[str]
    is_active: bool = Field(default=True)


class GamePerformance(SQLModel, table=True):
    __tablename__ = "games_performance"

    id: Optional[int] = Field(default=None, primary_key=True)

    performance_type_id: Optional[int] = _fk(
        "game_performance_types", col_type="smallint", index=True
    )
    performance_type: Optional["GamePerformanceType"] = Relationship(
        back_populates="gp"
    )

    cross_comparison_id: Optional[bool] = _fk(
        "cross_comparison_types", col_type="smallint", index=True
    )
    cross_comparison: Optional["CrossComparisonType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    comparison_id: Optional[int] = Field(
        default=None, foreign_key="comparison_types.id", index=True
    )
    comparison: Optional["ComparisonType"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={
            "cascade": "all,delete",
        },
    )

    aggregation_id: Optional[int] = Field(
        default=None, foreign_key="data_aggregation_types.id", index=True
    )
    aggregation: Optional["DataAggregationType"] = Relationship(
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

    data_type: List["PerformanceDataType"] = Relationship(
        back_populates="data_category",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    __tablename__ = "performance_data_categories"


class PerformanceDataType(SQLModel, table=True):
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
    data_type: Optional["PerformanceDataType"] = Relationship(back_populates="pwd")

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

    perfomance_table_id: Optional[int] = Field(
        default=None, foreign_key="performance_windows_table.id", index=True
    )
    perfomance_table: Optional["PerformanceWindowTable"] = Relationship(
        back_populates="window_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )

    @property
    def get_window_data(self) -> "PerformanceWindowTable":
        if self.is_empty:
            empty_fields = {field: None for field in PerformanceWindowField.ALL}
            if self.l_empty_mask:
                empty_fields.update(
                    EmptyMaskConverter.convert_from_mask_to_dict(
                        self.l_empty_mask, PerformanceWindowField.LANE
                    )
                )

            elif self.g_empty_mask:
                empty_fields.update(
                    EmptyMaskConverter.convert_from_mask_to_dict(
                        self.g_empty_mask, PerformanceWindowField.LANE
                    )
                )
            return PerformanceWindowTable(**empty_fields)
        else:
            return self.perfomance_table


class PerformanceWindowTable(SQLModel):
    __tablename__ = "performance_windows_table"

    id: Optional[int] = Field(default=None, primary_key=True)

    l2: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l4: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l6: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l8: condecimal(max_digits=10, decimal_places=2) = Field(default=None, nullable=True)
    l10: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    ltotal: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )

    g15: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    g30: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    g45: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    g60: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    g60plus: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    gtotal: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )


# PERFORMANCE TOTAL
class PerformanceTotalData(table=True):
    __tablename__ = "performance_totals_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    total_gold: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    total_xp: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    kills_per_min: condecimal(max_digits=8, decimal_places=7) = Field(nullable=False)
    kda: condecimal(max_digits=5, decimal_places=2) = Field(nullable=False)

    neutral_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    tower_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    courier_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )

    lane_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    hero_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    observer_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    sentry_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    roshan_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    runes_picked_up: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )

    ancient_kills: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    buyback_count: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    observer_uses: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    sentry_uses: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )

    lane_efficiency: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )
    lane_efficiency_pct: condecimal(max_digits=10, decimal_places=2) = Field(
        default=None, nullable=True
    )

    first_blood_claimed: condecimal(max_digits=5, decimal_places=2) = Field(
        default=None, nullable=True
    )
    first_kill_time: Optional[int]

    died_first: condecimal(max_digits=5, decimal_places=2) = Field(
        default=None, nullable=True
    )
    first_death_time: Optional[int]

    lost_tower_first: condecimal(max_digits=5, decimal_places=2) = Field(
        default=None, nullable=True
    )
    lost_tower_lane: Optional[int]
    lost_tower_time: Optional[int]

    destroyed_tower_first: condecimal(max_digits=5, decimal_places=2) = Field(
        default=None, nullable=True
    )
    destroyed_tower_lane: Optional[int]
    destroyed_tower_time: Optional[int]

    id: Optional[int] = Field(default=None, primary_key=True)

    game_performance_id: Optional[int] = Field(
        default=None, foreign_key="games_performance.id", index=True
    )
    game_performance: Optional["GamePerformance"] = Relationship(
        back_populates="total_data",
        sa_relationship_kwargs=sa_kwargs_setter(add_default=True, join_depth=0),
    )
