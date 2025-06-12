from sqlmodel import col

from models import Game, PlayerGameData, ComparisonType
from models.performance import PerformanceWindowTable, PerformanceWindowData, PerformanceTotalData, Performance
from models.performance_data_type import ByTeamType
from modules.query_creators.helpers import ModelList, JoinList, combine_select


def match_ccomparison_query_creator(
        calculation_type_id: int | None,
        positions: list,
        is_flat: bool | None = None,
        league_id: int | None = None,
        patch_id: int | None = None,
        **kwargs
) -> tuple:
    models = ModelList()
    joins = JoinList()
    if patch_id:
        game_where = Game.patch_id == patch_id
    elif league_id:
        game_where = Game.league_id == league_id
    else:
        raise ValueError("No league_id value or patch_id value provided")

    where = [
        game_where,
        Performance.type_id == Performance.const.game.MATCH_DATA_COMPARISON,
        ComparisonType.basic == True,
        ComparisonType.is_flat == is_flat,
        col(ComparisonType.pos_cpd_id).in_(positions),
    ]

    models.add(ComparisonType.player_cpd_id, 'player_cpd_id', True)
    models.add(ComparisonType.player_cps_id, 'player_cps_id', True)
    models.add(ComparisonType.hero_cpd_id, 'hero_cpd_id', True)
    models.add(ComparisonType.hero_cps_id, 'hero_cps_id', True)
    models.add(ComparisonType.pos_cpd_id, 'pos_cpd_id', True)
    models.add(ComparisonType.pos_cps_id, 'pos_cps_id', True)
    models.add(ComparisonType.facet_cpd_id, 'facet_cpd_id', True)
    models.add(ComparisonType.facet_cps_id, 'facet_cps_id', True)

    joins.add(Performance, ComparisonType.performance_id == Performance.id)
    joins.add(PlayerGameData, PlayerGameData.id == Performance.player_game_data_id)
    joins.add(Game, Game.id == PlayerGameData.game_id)

    if calculation_type_id:
        models.add(PerformanceWindowData.l_empty_mask, 'l_empty_mask', True)
        models.add(PerformanceWindowData.g_empty_mask, 'g_empty_mask', True)
        models.add(PerformanceWindowTable, 'window_table', True)

        joins.add(PerformanceWindowData, PerformanceWindowData.performance_id == Performance.id)

        joins.add(
            PerformanceWindowTable,
            PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
            True,
        )
        where.append(PerformanceWindowData.calc_type_id == calculation_type_id)

    else:
        models.add(PerformanceTotalData, 'total_data', True)
        joins.add(PerformanceTotalData, PerformanceTotalData.performance_id == Performance.id)

    return combine_select(models.get_models(), joins.data, where), models.get_names()


def team_ccomparison_query_creator(
        calculation_type_id: int | None,
        is_flat: bool | None = None,
        league_id: int | None = None,
        patch_id: int | None = None,
        **kwargs
) -> tuple:
    if patch_id:
        by_team_where = ByTeamType.patch_id == patch_id
    elif league_id:
        by_team_where = ByTeamType.league_id == league_id
    else:
        raise ValueError("No league_id value or patch_id value provided")

    models = ModelList()
    joins = JoinList()
    where = [
        Performance.type_id == Performance.const.team.TEAM_MATCH_DATA_COMPARISON,
        ByTeamType.is_flat == is_flat,
        by_team_where,
    ]

    models.add(ByTeamType.team_cpd_id, 'team_cpd_id', True)
    models.add(ByTeamType.team_cps_id, 'team_cps_id', True)
    models.add(ByTeamType.patch_id, 'patch_id', True)

    joins.add(Performance, ByTeamType.performance_id == Performance.id)

    if calculation_type_id:
        models.add(PerformanceWindowData.l_empty_mask, 'l_empty_mask', True)
        models.add(PerformanceWindowData.g_empty_mask, 'g_empty_mask', True)
        models.add(PerformanceWindowTable, 'window_table', True)

        joins.add(PerformanceWindowData, PerformanceWindowData.performance_id == Performance.id)

        joins.add(
            PerformanceWindowTable,
            PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
            True,
        )

        where.append(PerformanceWindowData.calc_type_id == calculation_type_id)
    else:
        models.add(PerformanceTotalData, 'total_data', True)
        joins.add(PerformanceTotalData, PerformanceTotalData.performance_id == Performance.id)

    return combine_select(models.get_models(), joins.data, where), models.get_names()
