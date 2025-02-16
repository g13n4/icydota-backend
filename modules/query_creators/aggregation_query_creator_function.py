from models import Game, PlayerGameData, ComparisonType
from models.performance import PerformanceWindowTable, PerformanceWindowData, PerformanceTotalData, GamePerformance
from modules.query_creators.helpers import ModelList, JoinList, combine_select


def aggregation_query_creator(
        league_id: int,
        data_calculation_id: int | None,
        comparison: bool = False,
        flat: bool | None = None
) -> tuple:
    models = ModelList()
    joins = JoinList()
    where = [Game.league_id == league_id]

    models.add(PlayerGameData.hero_id, 'hero_id', True)
    models.add(PlayerGameData.player_id, 'player_id', True)
    models.add(PlayerGameData.position_id, 'position_id', True)

    joins.add(PlayerGameData, PlayerGameData.id == GamePerformance.player_game_data_id)
    joins.add(Game, Game.id == PlayerGameData.game_id)

    if comparison:
        models.add(ComparisonType.flat, 'is_flat', True)

        joins.add(Game, Game.id == PlayerGameData.game_id)
        joins.add(ComparisonType, ComparisonType.id == GamePerformance.comparison_id)

        where.append(GamePerformance.type_id == GamePerformance.const.MATCH_DATA_COMPARISON)
        where.append(ComparisonType.basic == True)
        where.append(ComparisonType.flat == flat)
    else:
        where.append(GamePerformance.type_id == GamePerformance.const.MATCH_DATA)

    if data_calculation_id:
        models.add(PerformanceWindowData.l_empty_mask, 'l_empty_mask', True)
        models.add(PerformanceWindowData.g_empty_mask, 'g_empty_mask', True)
        models.add(PerformanceWindowTable, 'window_table', True)

        joins.insert(GamePerformance, PerformanceWindowData.game_performance_id == GamePerformance.id)

        joins.insert(
            PerformanceWindowTable,
            PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
            True,
            index=1,
        )

        where.append(PerformanceWindowData.data_calculation_id == data_calculation_id)
    else:
        models.add(PerformanceTotalData, 'total_data', True)
        joins.add(PerformanceTotalData, PerformanceTotalData.game_performance_id == GamePerformance.id)

    return combine_select(models.get_models(), joins.data, where), models.get_names()
