from sqlmodel import col

from models import Game, PlayerGameData, ComparisonType
from models.performance import PerformanceWindowTable, PerformanceWindowData, PerformanceTotalData, Performance
from modules.query_creators.helpers import ModelList, JoinList, combine_select


def aggregation_query_creator(
        league_id: int,
        data_calculation_id: int | None,
        positions: list,
        flat: bool | None = None
) -> tuple:
    models = ModelList()
    joins = JoinList()
    where = [
        Game.league_id == league_id,
        Performance.type_id == Performance.const.game.MATCH_DATA_COMPARISON,
        ComparisonType.basic == True,
        ComparisonType.flat == flat,
        col(ComparisonType.pos_cpd_id).in_(positions)
    ]

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

    models.add(ComparisonType.player_cpd_id, 'player_cpd_id', True)
    models.add(ComparisonType.player_cps_id, 'player_cps_id', True)
    models.add(ComparisonType.hero_cpd_id, 'hero_cpd_id', True)
    models.add(ComparisonType.hero_cps_id, 'hero_cps_id', True)
    models.add(ComparisonType.pos_cpd_id, 'pos_cpd_id', True)
    models.add(ComparisonType.pos_cps_id, 'pos_cps_id', True)

    joins.add(PlayerGameData, PlayerGameData.id == Performance.player_game_data_id)
    joins.add(Game, Game.id == PlayerGameData.game_id)
    joins.add(ComparisonType, ComparisonType.id == Performance.comparison_id)

    return combine_select(models.get_models(), joins.data, where), models.get_names()
