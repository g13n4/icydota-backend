from sqlalchemy.orm import aliased
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud.helpers import to_front_bool
from constants.performance.game_side import SidePerformance
from models import Game, SidePerformanceData, League, PlayerGameData, Player


async def _create_player_hero_dict(players_select_data) -> dict:
    output = dict()
    for game_id, is_dire, hero_id, nickname, position, *other in players_select_data:
        key_ = (game_id, is_dire)
        if key_ not in output:
            output[key_] = []

        output[key_].append({ "hero_id": hero_id, "position_id": position })
    return output


def _sort_func(item: dict):
    return item['position_id']

async def get_games_all(
        db_session: AsyncSession,
        league_id: int | None = None,
        patch_id: int | None = None,
        offset: int = 0
):
    if league_id is None and patch_id is None:
        raise TypeError("Parameter should be provided! League and Patch ids are empty!")
    elif (league_id and patch_id):
        raise TypeError("Only one parameter should be provided! Provided both League or Patch.")

    sent_side = aliased(SidePerformanceData)
    dire_side = aliased(SidePerformanceData)

    where_condition = Game.league_id == league_id if league_id else Game.patch_id == patch_id

    select_objs = [Game, dire_side, sent_side]
    if patch_id:
        select_objs.append(League.name)


    select_query = (select(*select_objs)
                    .join(sent_side, onclause=sent_side.game_id == Game.id)
                    .join(dire_side, onclause=dire_side.game_id == Game.id))

    if patch_id:
        select_query.join(League, onclause=Game.league_id == League.id).where(where_condition)
    else:
        select_query.where(where_condition)

    match_objs = await db_session.exec(select_query.order_by(Game.id.desc()).offset(offset))

    players_select = (select(
        Game.id,
        PlayerGameData.dire,
        PlayerGameData.hero_id,
        Player.nickname,
        PlayerGameData.position_id,
    ).join(Player, onclause=PlayerGameData.player_id == Player.account_id)
                      .join(Game, onclause=Game.id == PlayerGameData.game_id)
                      .where(where_condition).order_by(Game.id.desc()).offset(offset * 10)
                      )

    players_objs = await db_session.exec(players_select)
    hero_data = await _create_player_hero_dict(players_objs)

    output = []
    for game_obj, dire_side_obj, sent_side_obj, *league in match_objs.all():
        dire_side_dict = { }
        sent_side_dict = { }
        sent_heroes = hero_data[(game_obj.id, False)]
        dire_heroes = hero_data[(game_obj.id, True)]

        sent_heroes.sort(key=lambda hero_item: _sort_func(hero_item))
        dire_heroes.sort(key=lambda hero_item: _sort_func(hero_item), reverse=True)

        sent_name, dire_name = game_obj.name.split(' vs ')
        for item in SidePerformance.VALUES:
            for side_obj, side_dict in [
                (dire_side_obj, dire_side_dict),
                (sent_side_obj, sent_side_dict),
            ]:
                value = getattr(side_obj, item.name)
                side_dict[item.name] = {
                    "label": item.description,
                    "value": value if item.value_type is not bool else to_front_bool(value),
                }

        data = {
            "id": game_obj.id,
            "dire_won": game_obj.dire_win,
            "name_dire": dire_name,
            "name_sent": sent_name,
            "duration": f'{game_obj.duration // 60}:{game_obj.duration % 60:02}',
            "sent_heroes": sent_heroes,
            "dire_heroes": dire_heroes,
            "dire_data": dire_side_dict,
            "sent_data": sent_side_dict,
        }
        if league:
            data['league_name'] = league[0]

        output.append(data)

    return { "games": output }
