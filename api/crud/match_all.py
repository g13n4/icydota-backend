from sqlalchemy.orm import aliased
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud.helpers import to_front_bool
from constants.performance.game_side import SidePerformance
from models import Game, SidePerformanceData, League, PlayerGameData, Player, Performance, PerformanceTotalData
from models.game import GamePerformanceGraph
import orjson

def _to_kda_format(value: float) -> str:
    return str(int(value)) if value is not None else "-"


async def _create_player_hero_dict(players_select_data) -> dict:
    output = dict()
    for game_id, is_dire, hero_id, nickname, position, kill, death, assist, *other in players_select_data:
        key_ = (game_id, is_dire)
        if key_ not in output:
            output[key_] = []

        output[key_].append(
            {
                "hero_id": str(hero_id),
                "position_id": str(position),
                "nickname": nickname,
                "kda": "/".join(map(_to_kda_format, [kill, death, assist])),
            }
        )
    return output


def _value_comparison(dire_value: float, dire_sent: float, ):
    if dire_value == dire_sent:
        return None
    else:
        if dire_value > dire_sent:
            return True
        else:
            return False


def _sort_func(item: dict):
    return item['position_id']


async def get_games_all(
        db_session: AsyncSession,
        league_id: int | None = None,
        patch_id: int | None = None,
        limit: int = 48,
        offset: int = 0,
) -> list[dict]:
    if league_id is None and patch_id is None:
        raise TypeError("Parameter should be provided! League and Patch ids are empty!")
    elif (league_id and patch_id):
        raise TypeError("Only one parameter should be provided! Provided both League or Patch.")

    sent_side = aliased(SidePerformanceData)
    dire_side = aliased(SidePerformanceData)

    where_condition = Game.league_id == league_id if league_id else Game.patch_id == patch_id

    select_objs = [
        Game.id,
        Game.name,
        Game.dire_win,
        Game.duration,
        dire_side,
        sent_side,
        League.name,
        GamePerformanceGraph.gold_game,
        GamePerformanceGraph.xp_game,
    ]

    select_query = (
        select(*select_objs)
        .join(sent_side, onclause=sent_side.game_id == Game.id)
        .join(dire_side, onclause=dire_side.game_id == Game.id)
        .join(League, onclause=Game.league_id == League.id)
        .join(GamePerformanceGraph, onclause=Game.id == GamePerformanceGraph.game_id, isouter=True)
        .filter(sent_side.dire == False, dire_side.dire == True)
        .where(where_condition)
    )

    select_query = select_query.order_by(Game.id.desc()).offset(offset).limit(limit)

    match_objs = await db_session.exec(select_query)

    # ten players per team
    players_select = (
        select(
            Game.id,
            PlayerGameData.dire,
            PlayerGameData.hero_id,
            Player.nickname,
            PlayerGameData.position_id,
            PerformanceTotalData.hero_kills,
            PerformanceTotalData.deaths,
            PerformanceTotalData.assists,
        )
        .join(Player, onclause=PlayerGameData.player_id == Player.account_id)
        .join(Game, onclause=Game.id == PlayerGameData.game_id)
        .join(Performance, onclause=Performance.player_game_data_id == PlayerGameData.id)
        .filter(Performance.type_id == Performance.const.game.MATCH_DATA)
        .join(PerformanceTotalData, onclause=PerformanceTotalData.performance_id == Performance.id)
        .where(where_condition)
        .order_by(Game.id.desc()).offset(offset * 10).limit(limit * 10)
    )

    players_objs = await db_session.exec(players_select)
    hero_data = await _create_player_hero_dict(players_objs)

    output = []
    counter = 1
    for game_id, game_name, game_dire_win, game_duration, dire_side_obj, sent_side_obj, league_name, graph_gold, graph_xp in match_objs.all():
        dire_side_dict = { }
        sent_side_dict = { }
        comp_dict = { }
        sent_heroes = hero_data[(game_id, False)]
        dire_heroes = hero_data[(game_id, True)]
        graph_data = graph_gold and graph_xp and {
            "gold": orjson.loads(graph_gold),
            "xp": orjson.loads(graph_xp),
        }

        counter += 1
        sent_heroes.sort(key=lambda hero_item: _sort_func(hero_item))
        dire_heroes.sort(key=lambda hero_item: _sort_func(hero_item))

        sent_name, dire_name = game_name.split(' vs ')
        for item in SidePerformance.VALUES:
            dire_value = getattr(dire_side_obj, item.name)
            dire_side_dict[item.name] = str(dire_value) if item.value_type is not bool else to_front_bool(dire_value)

            sent_value = getattr(sent_side_obj, item.name)
            sent_side_dict[item.name] = str(sent_value) if item.value_type is not bool else to_front_bool(sent_value)

            comp_dict[item.name] = _value_comparison(dire_value, sent_value)

        data = {
            "id": str(game_id),
            "direWon": game_dire_win,
            "direName": dire_name,
            "sentName": sent_name,
            "duration": f'{game_duration // 60}:{game_duration % 60:02}',
            "sentHeroes": sent_heroes,
            "direHeroes": dire_heroes,
            "direData": dire_side_dict,
            "sentData": sent_side_dict,
            "compData": comp_dict,
            'leagueName': league_name,
        }

        if graph_data:
            data["graphData"] = graph_data

        output.append(data)

    return output
