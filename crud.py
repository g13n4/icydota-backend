# from sqlmodel.ext.asyncio.session import AsyncSession
import re
from typing import Dict, Any, Optional, List, Callable, Tuple

from functools import partial

from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import ComparisonType, DataAggregationType, PerformanceDataCategory
from models import Hero, Player, Position, League, Game
from models import PerformanceWindowData, GamePerformance, PlayerGameData, PerformanceTotalData, PerformanceDataType
from utils.translation_dictionary import PERFORMANCE_FIELD_DICT


TOTAL_FIELDS = PerformanceTotalData.schema()['properties'].keys()
WINDOW_FIELDS = PerformanceWindowData.schema()['properties'].keys()

TO_EXCLUDE_FOR_LANE = []
TO_EXCLUDE_FOR_GAME = []

for name in WINDOW_FIELDS:
    if not name.startswith('l'):
        TO_EXCLUDE_FOR_LANE.append(name)
    if not name.startswith('g'):
        TO_EXCLUDE_FOR_GAME.append(name)

id_search = re.compile(r'.*_?id$')

TOTAL_FIELDS_FILTERED = [x for x in TOTAL_FIELDS if not id_search.match(x)]
WINDOW_FIELDS_FILTERED = [x for x in WINDOW_FIELDS if not id_search.match(x)]


def _to_item(label, value, key, capitalise: bool) -> Dict[str, Any]:
    if capitalise:
        label = ' '.join([x.capitalize() for x in label.split('_')])

    return {'label': label, 'value': value, 'key': key}


async def get_field_types(field_type: str) -> list:
    if field_type == 'total':
        return [_to_item(x, x, x, True)
                for idx, x in enumerate(TOTAL_FIELDS_FILTERED)]
    else:
        return [_to_item(PERFORMANCE_FIELD_DICT[x], x, x, True)
                for idx, x in enumerate(WINDOW_FIELDS_FILTERED)]


async def get_items(db: AsyncSession, model, ):
    return await db.exec(select(model))


def _to_menu_item(key: str, label: str, children: List[dict] = None, disabled: bool = False, icon: str = None):
    item = {
        'key': key,
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
                       sorted_func: Optional[Callable] = None) -> Dict[str, Any]:
    output = _to_menu_item(key=item.id if id_is_key else f"{key_add}{item.id}",
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

        output['children'] = [_process_menu_item(item=x, include_disabled=include_disabled, **child_kwargs)
                              for x in children_objs
                              if _is_comparable_obj(x) or include_disabled]
        return output


async def get_categories_menu(db: AsyncSession, include_disabled: bool | None) -> list:
    categories = await db.exec(select(PerformanceDataCategory))
    child_params = {'id_is_key': True, }


    totals = [{"key": 'total', 'label': 'Total data'}]
    return totals + [_process_menu_item(x, 'c', 'data_type', include_disabled=include_disabled,
                                        child_kwargs=child_params) for x in categories.all()]


async def get_categories_both(db: AsyncSession):
    cats = await db.exec(select(PerformanceDataCategory))

    all_cats = [x for x in sorted(cats.all(), key=lambda item: item.name)]

    child_params = {'id_is_key': True, }
    pmi = partial(_process_menu_item, key_add='c', children_key='data_type',  child_kwargs=child_params,
                  sorted_func=lambda item: item.name)

    totals = [{"key": 'total', 'label': 'Total data'}]
    total_dict = {'total': 'Total data'}
    return (totals + [pmi(x, include_disabled=True, ) for x in all_cats],
            totals + [pmi(x, include_disabled=False,) for x in all_cats],
            {**total_dict, **{str(sub_cat.id): sub_cat.name for cat in all_cats for sub_cat in cat.data_type}} )


async def get_league_header(db: AsyncSession, ) -> list:
    leagues = await db.exec(select(League).order_by(League.id.desc()))
    return [_process_menu_item(item, id_is_key=True) for item in leagues.all()]


async def get_league_games(db_session: AsyncSession, league_id: int):
    league_objs = await (db_session.exec(select(Game)
                                         .where(Game.league_id == league_id)
                                         .order_by(Game.id)))

    return [{'value': str(league.id), 'label': league.name or str(league.id), } for league in league_objs.all()]


async def get_data_types_menu():
    return [
        {'label': 'Data', 'key': 'data'},
        {'label': 'Data comparison', 'key': 'data_comparison'},
        {'label': 'Aggregation ', 'key': 'aggregation'},
        {'label': 'Aggregation comparison', 'key': 'aggregation_comparison'},
        {'label': 'Cross-comparison', 'key': 'cross_comparison'}
    ]


def to_default_selected_key(list_: List[dict]) -> str:
    return str(list_[0]['key'])


async def get_default_menu_data(db: AsyncSession, ) -> Dict[str, Any]:
    leagues = await get_league_header(db)
    menu = await get_data_types_menu()
    sub_menu, sub_menu_comp, categories_dict = await get_categories_both(db)

    games = await get_league_games(db, league_id=leagues[0]['key'])
    total_fields = await get_field_types('total')
    window_fields = await get_field_types('window')


    return {
        'leagueMenu': leagues,
        'leagueGames': games,
        'menu': menu,
        'submenu': sub_menu,
        'submenuComparison': sub_menu_comp,
        'totalFields': total_fields,
        'windowFields': window_fields,
        'categoriesDict': categories_dict,
        'lastEditDate': '26/03/2024',
        'appVersion': '1.0',
        'loaded': True,
    }


# DATA FOR DB PROCESSING
def _processing_db_output(output,
                          item_fields: dict,
                          exclude: list = None,
                          exists_total: bool = False) -> Tuple[list, list, bool]:
    if exclude is None:
        exclude = []

    processed_output = []
    data_values_info = dict()
    for model_obj, *item_data in output.all():
        item = {k: item_data[v] for k, v in item_fields.items()}

        for model_obj_key, model_obj_value in model_obj.model_dump(exclude=set(exclude)).items():
            if (model_obj_key.lower() in ['game_performance_id', 'data_type_id', 'id'] or
                    (not exists_total and re.match(r'[g|l]total', model_obj_key, re.IGNORECASE))):
                continue

            item[model_obj_key] = model_obj_value

            # LOOKING FOR MIN AND MAX VALUES
            if model_obj_value is not None:
                # CREATE THE BASE DICT OR START COMPARING
                if model_obj_key not in data_values_info:
                    data_values_info[model_obj_key] = {
                        "max": model_obj_value,
                        "min": model_obj_value,
                        "diff": None, }
                else:
                    data_values_info[model_obj_key]["max"] = max(data_values_info[model_obj_key]["max"], model_obj_value)
                    data_values_info[model_obj_key]["min"] = min(data_values_info[model_obj_key]["min"], model_obj_value)

        processed_output.append(item)

    # LOOKING FOR DIFFERENCE VALUES
    total = False
    for value_info_key in data_values_info.keys():
        mvi_max = data_values_info[value_info_key]["max"]
        mvi_min = data_values_info[value_info_key]["min"]

        data_values_info[value_info_key]["diff"] = mvi_max - mvi_min
        if re.match(r'[g|l]total', value_info_key):
            total = True

    return processed_output, [{**v, 'col': k} for k, v in data_values_info.items()], total


async def get_performance_data(db_session: AsyncSession,
                               match_id: int,
                               data_type: int | str,
                               game_stage: str,
                               comparison: Optional[str],
                               flat: Optional[bool], ):
    clauses = [PlayerGameData.game_id == match_id]

    item_fields = {'position': 2,
                   'hero': 0,
                   'player': 1, }

    # TOTAL OR WINDOW DATA
    exclude = ['game_performance_id, id', 'data_type_id']
    if data_type == 'total':
        model = PerformanceTotalData
    else:
        if game_stage == 'lane':
            exclude.extend(TO_EXCLUDE_FOR_LANE)
        elif game_stage == 'game':
            exclude.extend(TO_EXCLUDE_FOR_GAME)

        model = PerformanceWindowData
        clauses.append(PerformanceWindowData.data_type_id == data_type)

    select_models = [model, Hero.name, Player.nickname, Position.name]
    if comparison == 'player':
        select_models.append(ComparisonType.pos_cps_id)
        item_fields['opponents_pos'] = 3

    # QUERY BUILDING
    select_query = (select(*select_models)
                    .join(GamePerformance, onclause=GamePerformance.id == model.game_performance_id)
                    .join(PlayerGameData, onclause=GamePerformance.player_game_data_id == PlayerGameData.id)
                    .join(Position, onclause=PlayerGameData.position_id == Position.id)
                    .join(Hero, onclause=PlayerGameData.hero_id == Hero.id)
                    .join(Player, onclause=PlayerGameData.player_id == Player.account_id))

    # COMPARISON CHECK
    if comparison in ["player", "general"]:
        select_query = select_query.join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id)
        clauses.extend([
            GamePerformance.is_comparison == True,
            GamePerformance.cross_comparison == False,
            ComparisonType.basic == (True if comparison == "player" else False),
            ComparisonType.flat == flat, ])

    else:
        clauses.append(GamePerformance.is_comparison == False)

    # FINAL QUERY
    select_query = select_query.where(*clauses)

    output = await db_session.exec(select_query)

    data, limits, total = _processing_db_output(output=output, exclude=exclude, item_fields=item_fields, )

    return data, limits, total


async def get_aggregated_performance_data(db_session: AsyncSession,
                                          league_id: int,
                                          aggregation_type: str,
                                          data_type: str | int,
                                          game_stage: str,
                                          comparison: Optional[str],
                                          flat: Optional[bool], ):
    agg_type_dict = {
        "position": Position.name,
        "hero": Hero.name,
        "player": Player.nickname,
    }


    clauses = [DataAggregationType.league_id == league_id,
               GamePerformance.is_aggregation == True, ]

    exclude = ['game_performance_id, id']
    # TOTAL OR WINDOW DATA
    if data_type == 'total':
        model = PerformanceTotalData
    else:
        if game_stage == 'lane':
            exclude.extend(TO_EXCLUDE_FOR_LANE)
        elif game_stage == 'game':
            exclude.extend(TO_EXCLUDE_FOR_GAME)

        model = PerformanceWindowData
        clauses.append(PerformanceWindowData.data_type_id == data_type)


    # QUERY BUILDING
    select_query = (select(*[model, agg_type_dict[aggregation_type]])
                    .join(GamePerformance)
                    .join(DataAggregationType))

    # COMPARISON
    if comparison in ["general"]:
        select_query = select_query.join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id)
        clauses.extend([
            GamePerformance.is_comparison == True,
            GamePerformance.cross_comparison == False,
            ComparisonType.flat == flat, ])
    else:
        clauses.append(GamePerformance.is_comparison == False)

    # AGGREGATION
    if aggregation_type == "position":
        select_query = select_query.join(Position, onclause=DataAggregationType.position_id == Position.id)
        clauses.append(DataAggregationType.by_position == True)
    elif aggregation_type == "player":
        select_query = select_query.join(Player, onclause=DataAggregationType.player_id == Player.account_id)
        clauses.append(DataAggregationType.by_player == True)
    else:
        select_query = select_query.join(Hero, onclause=DataAggregationType.hero_id == Hero.id)
        clauses.append(DataAggregationType.by_hero == True)

    # FINAL QUERY
    select_query = select_query.where(*clauses)

    output = await db_session.exec(select_query)

    data, limits, total = _processing_db_output(output=output, item_fields={aggregation_type: 0, }, exclude=exclude, )

    return data, limits, total


def _update_variable(dict_: dict, key_: int | str, new_var: int | str):
    dict_.update({key_: new_var})
    return dict_


def _order_dict(dict_: dict, field: str) -> dict:
    return {k: v for k, v in sorted(dict_.items(), key=lambda item: str(item[1][field]).lower(), )}


async def get_cross_comparison_performance_data(db_session: AsyncSession,
                                                league_id: int,
                                                aggregation_type: str,
                                                position: str,
                                                data_field: str,
                                                data_type: str | int,
                                                flat: bool, ):
    fields_dict = {
        "hero": [Hero.name, Hero.id,  DataAggregationType.hero_cross_cps_id],
        "player": [Player.nickname, Player.account_id,  DataAggregationType.player_cross_cps_id],
    }


    clauses = [DataAggregationType.league_id == league_id,
               GamePerformance.cross_comparison == True,
               ComparisonType.flat == flat, ]

    select_fields = fields_dict[aggregation_type]

    # TOTAL OR WINDOW DATA
    if data_type == 'total':
        model = PerformanceTotalData
    else:
        model = PerformanceWindowData
        clauses.append(model.data_type_id == data_type)

    select_fields.append(getattr(model, data_field))

    # QUERY BUILDING
    select_query = (select(*select_fields)
                    .join(GamePerformance, GamePerformance.id == model.game_performance_id)
                    .join(DataAggregationType, DataAggregationType.id == GamePerformance.aggregation_id)
                    .join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id))

    # AGGREGATION
    if aggregation_type == "player":
        select_query = select_query.join(Player, onclause=DataAggregationType.player_id == Player.account_id)
        clauses.append(DataAggregationType.pos_player_cross == True)
    else:
        select_query = select_query.join(Hero, onclause=DataAggregationType.hero_id == Hero.id)
        clauses.append(DataAggregationType.pos_hero_cross == True)

    if position == 'support':
        clauses.append(DataAggregationType.sup_cross == True)
    elif position == 'core':
        clauses.append(DataAggregationType.carry_cross == True)
    else:
        clauses.append(DataAggregationType.mid_cross == True)

    # FINAL QUERY
    select_query = select_query.where(*clauses)

    query_output = await db_session.exec(select_query)

    # REFORMATTED _processing_db_output
    output_dict = dict()
    data_values_info = dict()
    rename_dict = dict()
    # hero/player name | id in db | id in db of the comparans player/hero
    for this_actor, this_actor_id, this_cps, value in query_output.all():
        rename_dict[this_actor_id] = this_actor

        if this_actor not in output_dict:
            output_dict[this_actor] = {
                aggregation_type: this_actor,
            }
        output_dict[this_actor][this_cps] = value

        if not value:
            continue

        if this_cps not in data_values_info:
            data_values_info[this_cps] = {
                "max": value,
                "min": value,
                "diff": None, }
        else:
            data_values_info[this_cps]["max"] = max(
                data_values_info[this_cps]["max"], value)
            data_values_info[this_cps]["min"] = min(
                data_values_info[this_cps]["min"], value)

    # LOOKING FOR DIFFERENCE VALUES
    for value_info_key in data_values_info.keys():
        mvi_max = data_values_info[value_info_key]["max"]
        mvi_min = data_values_info[value_info_key]["min"]

        data_values_info[value_info_key]["diff"] = mvi_max - mvi_min

    ordered_names = sorted(rename_dict.values(), key=lambda x: (x).lower())
    # REMOVING OLD VALUES FROM DICTIONARY
    new_output = dict()
    for item_name, item in output_dict.items():
        temp_dict = dict()
        for k, v in item.items():  # id / value
            cps_name = rename_dict.get(k, k)
            temp_dict[cps_name] = v

        new_output[item_name] = {(o_name if o_name != item_name else aggregation_type):
                                     (temp_dict.get(o_name, None) if o_name != item_name else temp_dict[aggregation_type])
                                 for o_name in ordered_names }

    new_output = _order_dict(new_output, aggregation_type)

    return (new_output, [{**v, 'col': rename_dict[k]} for k, v in data_values_info.items()])
