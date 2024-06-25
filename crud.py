import copy
from typing import Dict, Any, Optional, List, Callable, Tuple

from sqlalchemy.orm import aliased
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api_helpers import LANE_FIELDS, GAME_FIELDS, WINDOW_FIELDS_FILTERED, TOTAL_FIELDS_FILTERED
from models import League, Game
from models import PerformanceDataCategory, GameData
from utils.sorting_rating import gamedata_sort_rating
from utils.translation_dictionary import PERFORMANCE_FIELD_DICT, GAMEDATA_FIELD_DICT
from utils.helpers import to_str_time

def _capitalize_name(name: str) -> str:
    return ' '.join([x.capitalize() for x in name.split('_')])


def _to_item(label, value, key, capitalise: bool) -> Dict[str, Any]:
    if capitalise:
        label = _capitalize_name(label)

    return {'label': label, 'value': value, 'key': key}


async def get_field_types(field_type: str, stage: bool = False) -> list | Tuple[list, list]:
    if field_type == 'total':
        return [_to_item(x, x, x, True)
                for idx, x in enumerate(TOTAL_FIELDS_FILTERED)]
    else:
        if stage:
            lane = [_to_item(PERFORMANCE_FIELD_DICT[x], x, x, True)
                    for idx, x in enumerate(LANE_FIELDS)]
            game = [_to_item(PERFORMANCE_FIELD_DICT[x], x, x, True)
                    for idx, x in enumerate(GAME_FIELDS)]
            return lane, game
        else:
            return [_to_item(PERFORMANCE_FIELD_DICT[x], x, x, True)
                    for idx, x in enumerate(WINDOW_FIELDS_FILTERED)]


async def get_items(db: AsyncSession, model, ):
    return await db.exec(select(model))


def _to_menu_item(id_: str, label: str, children: List[dict] = None, disabled: bool = False, icon: str = None):
    item = {
        'id': id_,
        'label': label,
        'disabled': disabled,
    }
    if icon:
        item['icon'] = icon
    if children:
        item['children'] = children
    return item


def _is_comparable_obj(obj) -> bool:
    return (hasattr(obj, 'is_comparable') and getattr(obj, 'is_comparable'))


def _process_menu_item(item, key_add: Optional[str] = None, children_key: Optional[str] = None, name_is_id: bool = False,
                       child_kwargs: Optional[dict] = None, id_is_key: bool = False, include_disabled: bool = True,
                       sorted_func: Optional[Callable] = None, depth: int = 0, turn_off_empty: bool = False) -> Dict[str, Any]:
    output = _to_menu_item(id_=item.id if id_is_key else f"{key_add}{item.id}",
                           label=item.id if name_is_id else item.name)

    if not children_key:
        return output
    else:
        if not child_kwargs:
            child_kwargs = {}
        if key_add not in child_kwargs:
            child_kwargs['key_add'] = children_key[:3]

        children_objs = getattr(item, children_key)
        if sorted_func is not None:
            children_objs = sorted(children_objs, key=sorted_func)

        output['children'] = [_process_menu_item(item=x, include_disabled=include_disabled, depth=depth+1,
                                                 **child_kwargs)
                              for x in children_objs
                              if _is_comparable_obj(x) or include_disabled]

        if turn_off_empty and not depth and not len(output['children']):
            output['disabled'] = True

        return output


async def get_categories_menu(db: AsyncSession, include_disabled: bool | None) -> list:
    categories = await db.exec(select(PerformanceDataCategory))
    child_params = {'id_is_key': True, }


    totals = [{"key": 0, 'label': 'Overview'}]
    return totals + [_process_menu_item(x, 'c', 'data_type', include_disabled=include_disabled,
                                        child_kwargs=child_params) for x in categories.all()]




async def _process_performance_data_category(db: AsyncSession):
    cats = await db.exec(select(PerformanceDataCategory))

    categories_dict = {0: 'Overview'}
    child_to_parent = dict()
    all_categories = [{
        'id': 0,
        'key': 'c-0',
        'label': 'Overview',
        'children': [],
    }]
    for cat in cats:
        cat_key = f'c-{cat.id}'
        cat_item = {
            'id': cat.id,
            'key': cat_key,
            'label': cat.label,
            'description': cat.description,  # TODO: ADD THIS TO FRONT
            'children': [],
        }
        for sub_cat in cat.data_type:
            sub_cat_item = {
            'id': sub_cat.id,
            'key': f's-{sub_cat.id}',
            'label': sub_cat.name,
            'parent': cat_key,
            }

            categories_dict[sub_cat.id] = sub_cat.name
            child_to_parent[sub_cat.id] = cat_key
            cat_item['children'].append(copy.deepcopy(sub_cat_item))

        all_categories.append(cat_item)

    return all_categories, child_to_parent, categories_dict


async def get_league_header(db: AsyncSession, ) -> list:
    leagues = await db.exec(select(League).order_by(League.id.desc()))

    return [{'id': league.id,
             'key': f'{league.id}',
             'label': league.name,
             'has_dates': league.has_dates,
             'start_date': league.start_date and to_str_time(league.start_date),
             'end_date': league.end_date and to_str_time(league.start_date),
             } for league in leagues.all()]


async def get_league_games(db_session: AsyncSession, league_id: int):
    league_objs = await (db_session.exec(select(Game)
                                         .where(Game.league_id == league_id)
                                         .order_by(Game.id)))

    return [{'value': str(league.id), 'label': league.name or str(league.id), } for league in league_objs.all()]


def _get_game_duration(duration: int) -> str:
    hours = duration // 60 * 60
    minutes = duration // 60
    seconds = duration % 60

    str_duration = f'{minutes}:{seconds:2}'

    if hours:
        str_duration = f'{hours}:{str_duration}'

    return str_duration


# ADDITIONAL GAME DATA LIST
def _process_bool(value: Any):
    if type(value) == bool:
        return 'Yes' if value else 'No'
    return value


def _get_bigger_side(sent_value: int | bool, dire_value2: int | bool) -> int:
    if type(sent_value) == bool or sent_value == dire_value2:
        return 0
    else:
        return 1 if sent_value > dire_value2 else 2


def _get_game_data(value_sent: int | bool, value_dire: int | bool) -> dict:
    sent = _process_bool(value_sent)
    dire = _process_bool(value_dire)
    bigger = _get_bigger_side(sent, dire)

    return {
        'bigger': bigger,
        'sent': sent,
        'dire': dire, }


def flatten_league_game(game: Game, sent: GameData, dire: GameData, ):
    sent_dict = sent.dict()
    dire_dict = dire.dict()

    sent_name, dire_name = game.name.split(' vs ')

    game_data_list = [{
        'id': f'{game.id}-{x}',
        'name': GAMEDATA_FIELD_DICT[x],
        **_get_game_data(sent_dict[x], dire_dict[x]),
    } for x in sent_dict.keys() if x.lower() not in ['id', 'sentry_kills', 'obs_kills', 'kpm']]

    game_data_list.sort(key=lambda x: gamedata_sort_rating(x['name'].lower()), reverse=True)

    return {
        'id': game.id,
        'dire_won': game.dire_win,
        'name_dire': dire_name,
        'name_sent': sent_name,
        'duration': f'{game.duration // 60}:{game.duration % 60:02}',
        'data': game_data_list,
    }


async def get_league_games_info(db_session: AsyncSession, league_id: int):
    dire = aliased(GameData)
    sent = aliased(GameData)

    game_objs = await (db_session.exec(select(Game, sent, dire, )
                                       .join(sent, onclause=sent.id == Game.sent_game_data_id)
                                       .join(dire, onclause=dire.id == Game.dire_game_data_id)
                                       .where(Game.league_id == league_id)
                                       .order_by(Game.id.desc())))

    return [flatten_league_game(*game) for game in game_objs.all()]


def to_default_selected_key(list_: List[dict]) -> str:
    return str(list_[0]['key'])


async def get_default_menu_data(db: AsyncSession, ) -> Dict[str, Any]:
    leagues = await get_league_header(db)
    sub_menu, sub_menu_parent, categories_dict = await _process_performance_data_category(db)

    total_fields = await get_field_types('total')
    lane_fields, game_fields = await get_field_types('window', stage=True)

    return {
        'leagueMenu': leagues,
        'submenu': sub_menu,
        'submenuParent': sub_menu_parent,
        'categoriesDict': categories_dict,
        'totalFields': total_fields,
        'windowLaneFields': lane_fields,
        'windowGameFields': game_fields,
        'isLoaded': True,
    }


def create_combined_field_item(field_name: str, pattern: str, fields_to_use: list):
    return {
        'pattern': pattern,
        'fields_to_use': fields_to_use,
        'field_name': field_name,
    }
