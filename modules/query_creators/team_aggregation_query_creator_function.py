from models.performance import PerformanceWindowTable, PerformanceWindowData, PerformanceTotalData, Performance
from models.performance_data_type import ByTeamType
from modules.query_creators.helpers import ModelList, JoinList, combine_select


def team_aggregation_query_creator(
        patch_id: int | None = None,
        league_id: int | None = None,
        calculation_type_id: int | None = None,
        is_comparison: bool = False,
        is_flat: bool | None = None
) -> tuple:
    models = ModelList()
    joins = JoinList()

    if patch_id:
        where = [ByTeamType.patch_id == patch_id]
    elif league_id:
        where = [ByTeamType.league_id == league_id]
    else:
        raise ValueError("No league_id value or patch_id value provided")

    models.add(ByTeamType.team_id, 'team_id', True)
    models.add(ByTeamType.team_cpd_id, 'team_cpd_id', True)

    joins.insert(Performance, ByTeamType.performance_id == Performance.id)

    where.append(ByTeamType.is_flat == is_flat)

    if is_comparison:
        where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_DATA_COMPARISON)
    else:
        where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_DATA)

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
