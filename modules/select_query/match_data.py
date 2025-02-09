from models import PlayerGameData, Hero, Player, Position
from models.performance import PerformanceTotalData, PerformanceWindowData, PerformanceWindowTable, GamePerformance
from modules.select_query.helpers import JoinList, combine_select


def match_data_query_constructor(match_id: int, data_type: int, **kwargs) -> tuple[list, JoinList, list]:
    models = []
    joins = JoinList()
    where = [PlayerGameData.game_id == match_id ]

    if data_type == 0:
        models.append(PerformanceTotalData)
        joins.add(GamePerformance, PerformanceTotalData.game_performance_id == GamePerformance.id)
    else:
        models.append(PerformanceWindowData)
        joins.add(GamePerformance, PerformanceWindowData.game_performance_id == GamePerformance.id)

        models.append(PerformanceWindowTable)
        joins.add(
            PerformanceWindowTable,
            PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
            True
        )
        where.append(PerformanceWindowData.data_type_id == data_type)


    models.append(PlayerGameData.dire)
    joins.add(PlayerGameData, GamePerformance.player_game_data_id == PlayerGameData.id)

    models.append(Position.name)
    joins.add(Position, PlayerGameData.position_id == Position.id)

    models.append(Hero.name)
    joins.add(Hero, PlayerGameData.hero_id == Hero.id)

    models.append(Player.nickname)
    joins.add(Player, PlayerGameData.player_id == Player.account_id)

    return models, joins, where


def get_match_data_query(match_id: int, data_type: int, **kwargs):
    models, joins, where = match_data_query_constructor(match_id, data_type, **kwargs)
    where.append(GamePerformance.performance_type_id == GamePerformance.const.MATCH_DATA)
    return combine_select(models.get_, joins, where)
