from models import Game, PlayerGameData, ComparisonType
from models.performance import PerformanceWindowTable, PerformanceWindowData, PerformanceTotalData, Performance
from models.performance_data_type import ByTeamType
from modules.query_creators.helpers import ModelList, JoinList, combine_select


def team_aggregation_query_creator(
        league_id: int,
        data_calculation_id: int | None,
        is_comparison: bool = False,
        is_flat: bool | None = None
) -> tuple:
    models = ModelList()
    joins = JoinList()
    where = [ByTeamType.league_id == league_id]

    models.add(ByTeamType.team_id, 'team_id', True)
    models.add(ByTeamType.team_cpd_id, 'team_cpd_id', True)

    joins.add(Performance, PlayerGameData.id == Performance.player_game_data_id)

    where.append(ByTeamType.is_flat == is_flat)
    if is_comparison:
        where.append(Performance.type_id == Performance.const.team.TEAM_MATCH)
    else:
        where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_COMPARISON)

    if data_calculation_id:
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

        where.append(PerformanceWindowData.data_calculation_id == data_calculation_id)
    else:
        models.add(PerformanceTotalData, 'total_data', True)
        joins.add(PerformanceTotalData, PerformanceTotalData.game_performance_id == Performance.id)

    return combine_select(models.get_models(), joins.data, where), models.get_names()
