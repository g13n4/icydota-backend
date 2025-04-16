from sqlmodel import col

from models import Game, PlayerGameData, ComparisonType
from models.performance import PerformanceWindowTable, PerformanceWindowData, PerformanceTotalData, Performance
from models.performance_data_type import ByTeamType
from modules.query_creators.helpers import ModelList, JoinList, combine_select


def match_ccomparison_query_creator(
        league_id: int,
        calculation_type_id: int | None,
        positions: list,
        is_flat: bool | None = None
) -> tuple:
    models = ModelList()
    joins = JoinList()
    where = [
        Game.league_id == league_id,
        Performance.type_id == Performance.const.game.MATCH_DATA_COMPARISON,
        ComparisonType.basic == True,
        ComparisonType.is_flat == is_flat,
        col(ComparisonType.pos_cpd_id).in_(positions),
    ]

    if calculation_type_id:
        models.add(PerformanceWindowData.l_empty_mask, 'l_empty_mask', True)
        models.add(PerformanceWindowData.g_empty_mask, 'g_empty_mask', True)
        models.add(PerformanceWindowTable, 'window_table', True)

        joins.insert(Performance, PerformanceWindowData.game_performance_id == Performance.id)

        joins.insert(
            PerformanceWindowTable,
            PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
            True,
            index=1,
        )

        where.append(PerformanceWindowData.calc_type_id == calculation_type_id)
    else:
        models.add(PerformanceTotalData, 'total_data', True)
        joins.add(PerformanceTotalData, PerformanceTotalData.game_performance_id == Performance.id)

    models.add(ComparisonType.player_cpd_id, 'player_cpd_id', True)
    models.add(ComparisonType.player_cps_id, 'player_cps_id', True)
    models.add(ComparisonType.hero_cpd_id, 'hero_cpd_id', True)
    models.add(ComparisonType.hero_cps_id, 'hero_cps_id', True)
    models.add(ComparisonType.pos_cpd_id, 'pos_cpd_id', True)
    models.add(ComparisonType.pos_cps_id, 'pos_cps_id', True)

    joins.add(PlayerGameData, PlayerGameData.id == Performance.player_game_data_id)
    joins.add(Game, Game.id == PlayerGameData.game_id)
    joins.add(ComparisonType, ComparisonType.performance_id == Performance.id)

    return combine_select(models.get_models(), joins.data, where), models.get_names()


def team_ccomparison_query_creator(
        league_id: int,
        calculation_type_id: int | None,
        positions: list,
        is_flat: bool | None = None
) -> tuple:
    models = ModelList()
    joins = JoinList()
    where = [
        Performance.type_id == Performance.const.team.TEAM_MATCH_COMPARISON,
        ByTeamType.is_flat == is_flat,
        ByTeamType.league_id == league_id,
        col(ComparisonType.pos_cpd_id).in_(positions),
    ]

    if calculation_type_id:
        models.add(PerformanceWindowData.l_empty_mask, 'l_empty_mask', True)
        models.add(PerformanceWindowData.g_empty_mask, 'g_empty_mask', True)
        models.add(PerformanceWindowTable, 'window_table', True)

        joins.insert(Performance, PerformanceWindowData.game_performance_id == Performance.id)

        joins.insert(
            PerformanceWindowTable,
            PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
            True,
            index=1,
        )

        where.append(PerformanceWindowData.calc_type_id == calculation_type_id)
    else:
        models.add(PerformanceTotalData, 'total_data', True)
        joins.add(PerformanceTotalData, PerformanceTotalData.game_performance_id == Performance.id)

    models.add(ByTeamType.team_cpd_id, 'team_cpd_id', True)
    models.add(ByTeamType.team_cps_id, 'team_cps_id', True)
    models.add(ByTeamType.patch_id, 'patch_id', True)

    joins.add(ByTeamType, ByTeamType.performance_id == Performance.id)

    return combine_select(models.get_models(), joins.data, where), models.get_names()
