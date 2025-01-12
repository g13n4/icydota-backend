from typing import Optional, ClassVar

from sqlmodel import Field, SQLModel

from constants.ranking_performance import PerformanceRankingConstant
from .helpers import _fk


class PerformanceRankingType(SQLModel, table=True):
    __tablename__ = "performance_ranking_types"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_active: bool = Field(default=True)

    const: ClassVar[PerformanceRankingConstant] = PerformanceRankingConstant


class PerformanceRanking(SQLModel, table=True):
    __tablename__ = "performance_ranking_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    performance_ranking_type_id: Optional[int] = Field(
        default=None, foreign_key="performance_ranking_types.id", index=True
    )

    player_id: Optional[int] = Field(
        default=None, foreign_key="players.account_id", index=True
    )
    hero_id: Optional[int] = Field(default=None, foreign_key="heroes.id", index=True)

    team_id: Optional[int] = Field(default=None, foreign_key="teams.id", index=True)
    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)


class PerformanceWindowRanking(SQLModel, table=True):
    __tablename__ = "performance_windows_ranking_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    window_field_id: Optional[int] = _fk(
        "performance_window_fields", col_type="smallint"
    )
    performance_ranking_id: Optional[int] = Field(
        default=None, foreign_key="performance_ranking_data.id"
    )
    performance_window_data_id: Optional[int] = Field(
        default=None, foreign_key="performance_windows_data.id"
    )


class PerformanceTotalRanking(SQLModel, table=True):
    __tablename__ = "performance_totals_ranking_data"

    id: Optional[int] = Field(default=None, primary_key=True)

    total_field_id: Optional[int] = _fk("performance_total_fields", col_type="smallint")
    performance_ranking_id: Optional[int] = Field(
        default=None, foreign_key="performance_ranking_data.id"
    )
    performance_total_data_id: Optional[int] = Field(
        default=None, foreign_key="performance_totals_data.id"
    )
