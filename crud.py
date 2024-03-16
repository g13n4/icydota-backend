# from sqlmodel.ext.asyncio.session import AsyncSession
import copy
import re
from typing import Dict, Any, Optional, List, Callable, Tuple

from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import ComparisonType, DataAggregationType
from models import Hero, Player, Position
from models import PerformanceWindowData, GamePerformance, PlayerGameData, PerformanceTotalData, PerformanceDataType


TOTAL_FIELDS = PerformanceTotalData.schema()['properties'].keys()
WINDOW_FIELDS = PerformanceWindowData.schema()['properties'].keys()

TO_EXCLUDE_FOR_LANE = []
TO_EXCLUDE_FOR_GAME = []

for name in WINDOW_FIELDS:
    if not name.startswith('l'):
        TO_EXCLUDE_FOR_LANE.append(name)
    if not name.startswith('g'):
        TO_EXCLUDE_FOR_GAME.append(name)


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


def _process_menu_item(item, key_add: Optional[str], children_key: Optional[str] = None, name_is_id: bool = False,
                       child_kwargs: Optional[dict] = None, id_is_key: bool = False, include_disabled: bool = True) -> Dict[str, Any]:
    output = _to_menu_item(key=item.id if id_is_key else f"{key_add}{item.id}",
                           label=item.id if name_is_id else item.name)

    if not children_key:
        return output
    else:
        if not child_kwargs:
            child_kwargs = {}
        if key_add not in child_kwargs:
            child_kwargs['key_add'] = children_key[:3]

        output['children'] = [_process_menu_item(item=x, include_disabled=include_disabled, **child_kwargs)
                              for x in getattr(item, children_key)
                              if not (hasattr(x, 'disabled') and getattr(x, 'disabled') and not include_disabled)]
        return output


async def get_categories_menu(db: AsyncSession, model, include_disabled: bool | None) -> list:
    categories = await db.exec(select(model))
    child_params = {
        'id_is_key': True, }


    totals = [{"key": 'total', 'label': 'Total data'}]
    return totals + [_process_menu_item(x, 'c', 'data_type', include_disabled=include_disabled,
                                        child_kwargs=child_params) for x in categories.all()]


async def get_league_header(db: AsyncSession, league_model, ) -> list:
    leagues = await db.exec(select(league_model).order_by(league_model.id.desc()))
    return [_process_menu_item(item, 'l', id_is_key=True) for item in leagues]


async def get_league_games(db_session: AsyncSession, game_model, league_id: int):
    league_objs = (db_session.exec(select(game_model)
                                   .where(game_model.league_id == league_id)
                                   .order_by(game_model.id)))

    return [{'value': league.id, 'label': league.name or league.id, } for league in league_objs.all()]


async def get_data_types_menu():
    return [
        {'label': 'Data', 'value': 'data', 'key': 'data'},
        {'label': 'Data comparison', 'value': 'data_comparison', 'key': 'data_comparison'},
        {'label': 'Aggregation ', 'value': 'aggregation', 'key': 'aggregation'},
        {'label': 'Aggregation comparison', 'value': 'aggregation_comparison', 'key': 'aggregation_comparison'},
        {'label': 'Cross-comparison', 'value': 'aggregation_cross_comparison', 'key': 'aggregation_cross_comparison'}
    ]


# DATA FOR DB PROCESSING
def _processing_db_output(output, item_fields: dict, exclude: list = None, exists_total: bool = False) -> Tuple[list, list]:
    if exclude is None:
        exclude = []

    processed_output = []
    data_values_info = dict()
    for model_obj, *item_data in output.all():
        item = {k: item_data[v] for k, v in item_fields.items()}

        for model_obj_key, model_obj_value in model_obj.model_dump(exclude=set(exclude)).items():
            if (model_obj_key.lower() in ['game_performance_id', 'id'] or
                    (not exists_total and re.match(r'[g|l]total',model_obj_key, re.IGNORECASE ))):
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
    for value_info_key in data_values_info.keys():
        mvi_max = data_values_info[value_info_key]["max"]
        mvi_min = data_values_info[value_info_key]["min"]

        data_values_info[value_info_key]["diff"] = mvi_max - mvi_min

    return processed_output, [{**v, 'col': k} for k, v in data_values_info.items()]


async def get_performance_data(db_session: AsyncSession,
                               match_id: int,
                               data_type: int | str,
                               lane_data: Optional[bool],
                               comparison: Optional[str],
                               flat: Optional[bool], ):
    clauses = [PlayerGameData.game_id == match_id]
    total = None

    item_fields = {'position': 2,
                   'hero': 0,
                   'player': 1, }

    # TOTAL OR WINDOW DATA
    exclude = ['game_performance_id, id']
    if data_type == 'total':
        model = PerformanceTotalData
    else:
        dt_obj = await db_session.get(PerformanceDataType, data_type)
        total = dt_obj.sum_to_agg
        if lane_data:
            exclude.extend(TO_EXCLUDE_FOR_LANE)
        else:
            exclude.extend(TO_EXCLUDE_FOR_GAME)

        model = PerformanceWindowData
        clauses.append(PerformanceWindowData.data_type_id == data_type)

    select_models = [model, Hero.name, Player.nickname, Position.name]
    if comparison == 'player':
        select_models = [model, Hero.name, Player.nickname, Position.name, ComparisonType.pos_cps_id]
        item_fields['opponents_pos'] = 3

    # QUERY BUILDING
    select_query = (select(*select_models)
                    .join(GamePerformance, onclause=GamePerformance.id==model.game_performance_id)
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

    data, limits = _processing_db_output(output=output, exclude=exclude, item_fields=item_fields,
                                         exists_total=total is None)

    return data, limits, total


async def get_aggregated_performance_data(db_session: AsyncSession,
                                          league_id: int,
                                          aggregation_type: str,
                                          data_type: str | int,
                                          lane_data: Optional[bool],
                                          comparison: Optional[str],
                                          flat: Optional[bool], ):
    total = None
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
        dt_obj = await db_session.get(PerformanceDataType, data_type)
        total = dt_obj.sum_to_agg
        if lane_data:
            exclude.extend(TO_EXCLUDE_FOR_LANE)
        else:
            exclude.extend(TO_EXCLUDE_FOR_GAME)

        model = PerformanceWindowData
        clauses.append(PerformanceWindowData.data_type_id == data_type)


    # QUERY BUILDING
    select_query = (select(*[model, agg_type_dict[aggregation_type]])
                    .join(GamePerformance)
                    .join(DataAggregationType))

    # COMPARISON
    if comparison in ["player", "general"]:
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

    data, limits = _processing_db_output(output=output, item_fields={aggregation_type: 0, }, exclude=exclude,
                                         exists_total=total is None)

    return data, limits, total


def _update_variable(dict_: dict, key_: int | str, new_var: int | str):
    dict_.update({key_: new_var})
    return dict_


def _order_dict(dict_) -> dict:
    return {k: v for k, v in sorted(dict_.items(), key=lambda item: item[1]['player'])}


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
    join_clause = GamePerformance.id == model.game_performance_id


    # QUERY BUILDING
    select_query = (select(*select_fields)
                    .join(GamePerformance, join_clause)
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
    elif position == 'carry':
        clauses.append(DataAggregationType.carry_cross == True)
    else:
        clauses.append(DataAggregationType.mid_cross == True)

    # FINAL QUERY
    select_query = select_query.where(*clauses)

    query_output = await db_session.exec(select_query)

    # REFORMATTED _processing_db_output
    output_dict = {}
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

    ordered_names = sorted([act_name for act_name in rename_dict.values()])
    # REMOVING OLD VALUES FROM DICTIONARY
    new_output = dict()
    for item_name, item in output_dict.items():
        temp_dict = dict()
        for k, v in item.items():
            cps_name = rename_dict.get(k, k)
            temp_dict[cps_name] = v

        new_output[item_name] = temp_dict

    new_output = _order_dict(new_output)

    return (new_output, [{**v, 'col': rename_dict[k]} for k, v in data_values_info.items()])
