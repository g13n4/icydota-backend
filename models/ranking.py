from typing import Optional

from helpers import _fk
from sqlmodel import Field, SQLModel


class PerformanceRankingType(SQLModel, table=True):
    __tablename__ = "performance_ranking_types"

    PLAYER_MATCH_RANK = 1
    PLAYER_MATCH_BEST_RANK = 2
    PLAYER_MATCH_AVG_RANK = 3
    PLAYER_MATCH_COMPARISON_RANK = 4
    PLAYER_MATCH_COMPARISON_BEST_RANK = 5
    PLAYER_MATCH_COMPARISON_AVG_RANK = 6

    HERO_MATCH_RANK = 7
    HERO_MATCH_BEST_RANK = 8
    HERO_MATCH_AVG_RANK = 9
    HERO_MATCH_COMPARISON_RANK = 10
    HERO_MATCH_COMPARISON_BEST_RANK = 11

    TEAM_RANK = 12
    TEAM_BEST_RANK = 13

    LEAGUE_RANK = 14
    LEAGUE_BEST_RANK = 15

    PLAYER_AGGREGATED_RANK = 16
    HERO_AGGREGATED_RANK = 17

    PLAYER_AGGREGATED_COMPARISON_RANK = 18
    HERO_AGGREGATED_COMPARISON_RANK = 19

    TYPES = [
        (PLAYER_MATCH_RANK, "Player Match Rank"),
        (PLAYER_MATCH_BEST_RANK, "Player Match Best Rank"),
        (PLAYER_MATCH_AVG_RANK, "Player Match Avg Rank"),
        (PLAYER_MATCH_COMPARISON_RANK, "Player Match Comparison Rank"),
        (PLAYER_MATCH_COMPARISON_BEST_RANK, "Player Match Comparison Best Rank"),
        (PLAYER_MATCH_COMPARISON_AVG_RANK, "Player Match Comparison Avg Rank"),
        (HERO_MATCH_RANK, "Hero Match Rank"),
        (HERO_MATCH_BEST_RANK, "Hero Match Best Rank"),
        (HERO_MATCH_AVG_RANK, "Hero Match Avg Rank"),
        (HERO_MATCH_COMPARISON_RANK, "Hero Match Comparison Rank"),
        (HERO_MATCH_COMPARISON_BEST_RANK, "Hero Match Comparison Best Rank"),
        (TEAM_RANK, "Team Rank"),
        (TEAM_BEST_RANK, "Team Best Rank"),
        (LEAGUE_RANK, "League Rank"),
        (LEAGUE_BEST_RANK, "League Best Rank"),
        (PLAYER_AGGREGATED_RANK, "Player Aggregated Rank"),
        (HERO_AGGREGATED_RANK, "Hero Aggregated Rank"),
        (PLAYER_AGGREGATED_COMPARISON_RANK, "Player Aggregated Comparison Rank"),
        (HERO_AGGREGATED_COMPARISON_RANK, "Hero Aggregated Comparison Rank"),
    ]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_active: bool = Field(default=True)


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
