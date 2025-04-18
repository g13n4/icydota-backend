from models import Game, PlayerGameData, ComparisonType
from models.performance import PerformanceWindowTable, PerformanceWindowData, PerformanceTotalData, Performance
from modules.query_creators.helpers import ModelList, JoinList, combine_select


def match_aggregation_query_creator(
        league_id: int,
        calculation_type_id: int | None,
        is_comparison: bool = False,
        is_flat: bool | None = None
) -> tuple:
    models = ModelList()
    joins = JoinList()
    where = [Game.league_id == league_id]

    models.add(PlayerGameData.hero_id, 'hero_id', True)
    models.add(PlayerGameData.player_id, 'player_id', True)
    models.add(PlayerGameData.position_id, 'position_id', True)
    models.add(PlayerGameData.facet_id, 'facet_id', True)

    joins.add(Performance, PlayerGameData.id == Performance.player_game_data_id)
    joins.add(Game, Game.id == PlayerGameData.game_id)

    if is_comparison:
        models.add(ComparisonType.is_flat, 'is_flat', True)

        joins.add(ComparisonType, ComparisonType.performance_id == Performance.id)

        where.append(Performance.type_id == Performance.const.game.MATCH_DATA_COMPARISON)
        where.append(ComparisonType.basic == True)
        where.append(ComparisonType.is_flat == is_flat)
    else:
        where.append(Performance.type_id == Performance.const.game.MATCH_DATA)

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
